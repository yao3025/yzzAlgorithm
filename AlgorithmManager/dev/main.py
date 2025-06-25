import os
os.environ['QT_API'] = 'pyside6'  # 确保 qtpy 使用 pyside6
import warnings
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QTextEdit, QDialog, QFormLayout, QDialogButtonBox, QSpinBox, QListWidget, QListWidgetItem, QPlainTextEdit
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QIcon
import qdarkstyle
import shutil, subprocess

# 预览对话框
class PreviewDialog(QDialog):
    def __init__(self, parent=None, title="", text="", editable=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(not editable)
        layout.addWidget(self.text_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_text(self):
        return self.text_edit.toPlainText()

# 参数设置对话框（CMake 参数）
class ParamsDialog(QDialog):
    def __init__(self, parent=None, alg_name="", alg_dir=""):
        super().__init__(parent)
        self.alg_name = alg_name
        self.alg_dir = alg_dir
        # 前置获取：系统 CMake 可执行文件与版本
        self.default_cmake_path = shutil.which("cmake") or ""
        try:
            out = subprocess.check_output([self.default_cmake_path, "--version"], universal_newlines=True)
            self.system_cmake_version = out.splitlines()[0]
        except Exception:
            self.system_cmake_version = ""
        # 检测 GCC 编译器
        self.default_gpp = shutil.which("g++") or ""

        self.setWindowTitle("CMake 参数设置")
        self.resize(500, 500)
        layout = QFormLayout(self)

        # CMake 版本要求
        self.edit_cmake_version = QLineEdit(self.system_cmake_version)
        layout.addRow("CMake 版本要求：", self.edit_cmake_version)

        # 项目名称
        self.edit_project_name = QLineEdit(alg_name)
        layout.addRow("项目名称：", self.edit_project_name)

        # C++ 标准
        self.spin_cxx_standard = QSpinBox()
        self.spin_cxx_standard.setRange(11, 23)
        self.spin_cxx_standard.setValue(17)
        layout.addRow("C++ 标准：", self.spin_cxx_standard)

        # 添加可执行程序（仅包含根目录 main.cpp 及 src 目录下的 .cpp 文件）
        self.list_execs = QListWidget()
        # 根目录
        root_main = os.path.join(alg_dir, "main.cpp")
        if os.path.exists(root_main):
            item = QListWidgetItem("main.cpp")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.list_execs.addItem(item)
        # src 目录
        src_dir = os.path.join(alg_dir, "src")
        if os.path.isdir(src_dir):
            for f in os.listdir(src_dir):
                if f.endswith(".cpp"):
                    rel = os.path.join("src", f).replace("\\", "/")
                    item = QListWidgetItem(rel)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Checked)
                    self.list_execs.addItem(item)
        layout.addRow("添加可执行程序：", self.list_execs)

        # 编译环境（从系统环境变量中获取）
        self.combo_env = QComboBox()
        envs = ["MSVC"]
        if self.default_gpp:
            envs.append("GCC")
        envs.append("手动")
        self.combo_env.addItems(envs)
        layout.addRow("编译环境：", self.combo_env)
        # 编译器路径展示或输入框
        self.edit_custom_compiler = QLineEdit()
        self.edit_custom_compiler.setEnabled(False)
        layout.addRow("编译器路径：", self.edit_custom_compiler)
        # 目标架构选择
        self.combo_arch = QComboBox()
        self.combo_arch.addItems(["x86", "x64"])
        self.combo_arch.setCurrentText("x64")
        layout.addRow("目标架构：", self.combo_arch)
        def on_env_changed(idx):
            env = self.combo_env.currentText()
            if env == "MSVC":
                # 从系统 PATH 查找 cl
                self.edit_custom_compiler.setText(shutil.which("cl") or "")
                self.edit_custom_compiler.setEnabled(False)
            elif env == "GCC":
                self.edit_custom_compiler.setText(self.default_gpp)
                self.edit_custom_compiler.setEnabled(False)
            else:
                # 手动输入
                self.edit_custom_compiler.setText("")
                self.edit_custom_compiler.setEnabled(True)
        self.combo_env.currentIndexChanged.connect(on_env_changed)
        on_env_changed(0)

        # 预览按钮
        self.btn_preview_cmake = QPushButton("预览 CMakeLists.txt")
        self.btn_preview_cmd = QPushButton("预览 编译命令")
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_preview_cmake)
        hbox.addWidget(self.btn_preview_cmd)
        layout.addRow(hbox)

        # 确认/取消
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        self.btn_preview_cmake.clicked.connect(self.on_preview_cmake)
        self.btn_preview_cmd.clicked.connect(self.on_preview_cmd)

    def on_preview_cmake(self):
        content = self.generate_cmakelists()
        dlg = PreviewDialog(self, "CMakeLists.txt 预览", content, editable=True)
        if dlg.exec() == QDialog.Accepted:
            self.preview_cmakelists = dlg.get_text()

    def on_preview_cmd(self):
        cmd = self.generate_compile_cmd()
        dlg = PreviewDialog(self, "编译命令 预览", cmd, editable=True)
        if dlg.exec() == QDialog.Accepted:
            self.preview_cmd = dlg.get_text()

    def generate_cmakelists(self):
        lines = []
        lines.append(f"cmake_minimum_required(VERSION {self.edit_cmake_version.text()})")
        lines.append(f"project({self.edit_project_name.text()})")
        lines.append(f"set(CMAKE_CXX_STANDARD {self.spin_cxx_standard.value()})")
        lines.append("set(CMAKE_CXX_STANDARD_REQUIRED ON)")
        for i in range(self.list_execs.count()):
            item = self.list_execs.item(i)
            if item.checkState() == Qt.Checked:
                src = item.text()
                name = os.path.splitext(os.path.basename(src))[0]
                lines.append(f"add_executable({name} {src})")
        return "\n".join(lines)

    def generate_compile_cmd(self):
        parts = []
        if self.combo_env.currentText() == "MSVC" and self.default_cmake_path:
            parts.append(f"pushd {os.path.dirname(self.default_cmake_path)}")
            parts.append(f"call {self.edit_custom_compiler.text()}")
            parts.append("popd")
        parts.append(f"cd {self.alg_dir}/build")
        parts.append(f"cmake -S {self.alg_dir} -B {self.alg_dir}/build -DCMAKE_BUILD_TYPE={self.spin_cxx_standard.value()}")
        parts.append(f"cmake --build {self.alg_dir}/build --config {self.spin_cxx_standard.value()}")
        return "\n".join(parts)

    def get_params(self):
        return {
            "cmake_version_req": self.edit_cmake_version.text(),
            "project_name": self.edit_project_name.text(),
            "cxx_standard": self.spin_cxx_standard.value(),
            "execs": [self.list_execs.item(i).text() for i in range(self.list_execs.count()) if self.list_execs.item(i).checkState() == Qt.Checked],
            "env": self.combo_env.currentText(),
            "compiler_path": self.edit_custom_compiler.text(),
            "preview_cmakelists": getattr(self, "preview_cmakelists", None),
            "preview_cmd": getattr(self, "preview_cmd", None),
            "cmake_path": self.default_cmake_path,
            "arch": self.combo_arch.currentText()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口标题和图标
        self.setWindowTitle("算法管理程序")
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "img", "icon.png"))
        self.setWindowIcon(QIcon(icon_path))
        self.resize(800, 600)
        self.setup_ui()
        self.populate_algorithms()

        # 默认参数
        self.params = {
            "env": "MSVC",
            "compiler_path": r"",
            "cmake_path": shutil.which("cmake") or "cmake",
            "build_type": "Release",
            "vsvars_path": r"",
            "arch": "x64"
        }

    def setup_ui(self):
        # 顶部布局：算法选择、参数设置按钮、编译运行按钮
        label_alg = QLabel("算法：")
        self.combo_alg = QComboBox()
        self.btn_set_params = QPushButton("设置参数")
        self.btn_clear_log = QPushButton("清空日志")
        self.btn_build = QPushButton("编译并运行")

        top_layout = QHBoxLayout()
        top_layout.addWidget(label_alg)
        top_layout.addWidget(self.combo_alg)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_set_params)
        top_layout.addWidget(self.btn_clear_log)
        top_layout.addWidget(self.btn_build)

        # 底部日志输出
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.log_output)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # 信号连接
        self.btn_set_params.clicked.connect(self.open_params_dialog)
        self.btn_clear_log.clicked.connect(self.log_output.clear)
        self.btn_build.clicked.connect(self.on_build)

    def populate_algorithms(self):
        # 项目根目录：打包后优先使用 sys._MEIPASS，否则使用相对路径
        if getattr(sys, 'frozen', False):
            # 已打包，可执行文件所在目录即项目根目录
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        for name in os.listdir(root):
            path = os.path.join(root, name)
            # 目录名以序号_算法名格式
            if os.path.isdir(path) and name and name[0].isdigit() and "_" in name:
                self.combo_alg.addItem(name)

    def open_params_dialog(self):
        alg = self.combo_alg.currentText()
        # 计算项目根目录
        if getattr(sys, 'frozen', False):
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        alg_dir = os.path.join(root, alg)
        dialog = ParamsDialog(self, alg, alg_dir)
        if dialog.exec() == QDialog.Accepted:
            newp = dialog.get_params()
            self.params.update(newp)
            self.log_output.append(f"CMake 参数已设置：版本要求={newp['cmake_version_req']}，项目名={newp['project_name']}，C++标准={newp['cxx_standard']}，可执行文件={','.join(newp['execs'])}，环境={newp['env']}")

    def on_build(self):
        # 使用对话框中设置的参数
        cmake_exec = self.params.get("cmake_path", "cmake")
        build_type = self.params.get("build_type", "Release")
        env = self.params.get("env")
        # 根据环境选择编译器路径
        compiler = self.params.get("compiler_path", "")
        if env == "MSVC":
            compiler = shutil.which("cl") or compiler
        elif env == "GCC":
            compiler = compiler or shutil.which("g++")
        # 日志输出使用的环境和编译器
        self.log_output.append(f"使用 {env} 编译环境，编译器：{compiler}")
        alg = self.combo_alg.currentText()
        # 计算项目根目录
        if getattr(sys, 'frozen', False):
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        alg_dir = os.path.join(root, alg)
        # 检测 CMakeLists.txt
        cmk = os.path.join(alg_dir, "CMakeLists.txt")
        if not os.path.exists(cmk):
            with open(cmk, "w", encoding="utf-8") as f:
                pass
            self.log_output.append("未检测到 CMakeLists.txt，已创建空文件")
        else:
            self.log_output.append("检测到 CMakeLists.txt")
        build_dir = os.path.join(alg_dir, "build")
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        # 创建 build 目录
        os.makedirs(build_dir)
        # 构建参数
        arch = self.params.get('arch', 'x64')
        # 选择生成器
        if env == "GCC": generator = "MinGW Makefiles"
        else: generator = "Visual Studio 16 2019"
        # 组装 config 参数列表
        cfg_args = [cmake_exec, "-G", generator, "-S", alg_dir, "-B", build_dir, f"-DCMAKE_BUILD_TYPE={build_type}"]
        if env != "GCC": cfg_args += ["-A", arch]
        else: cfg_args += ["-DCMAKE_CXX_FLAGS=-m32"] if arch=="x86" else ["-DCMAKE_CXX_FLAGS=-m64"]
        if compiler:
            comp_path = compiler.replace('\\','/')
            cfg_args.append(f"-DCMAKE_CXX_COMPILER={comp_path}")
        # 异步执行配置
        self.log_output.append(f"开始配置：生成器={generator}, 构建类型={build_type}, 架构={arch} ...")
        self.config_proc = QProcess(self)
        self.config_proc.setWorkingDirectory(root)
        self.config_proc.readyReadStandardOutput.connect(lambda: self.handle_output(self.config_proc, False))
        self.config_proc.readyReadStandardError.connect(lambda: self.handle_output(self.config_proc, True))
        self.config_proc.finished.connect(lambda code, status: self._on_config_finished(code, status, cmake_exec, build_dir, build_type, env, compiler, root))
        self.config_proc.start(cmake_exec, cfg_args[1:])

    def _on_config_finished(self, code, status, cmake_exec, build_dir, build_type, env, compiler, root):
        if code != 0:
            self.log_output.append(f"配置失败，返回码：{code}")
            return
        # 异步执行构建
        self.log_output.append("配置完成，开始构建...")
        build_args = [cmake_exec, "--build", build_dir]
        if env != "GCC": build_args += ["--config", build_type]
        self.build_proc = QProcess(self)
        self.build_proc.setWorkingDirectory(root)
        self.build_proc.readyReadStandardOutput.connect(lambda: self.handle_output(self.build_proc, False))
        self.build_proc.readyReadStandardError.connect(lambda: self.handle_output(self.build_proc, True))
        self.build_proc.finished.connect(lambda code, status: self._on_build_finished(code, status, build_dir))
        self.build_proc.start(build_args[0], build_args[1:])

    def _on_build_finished(self, code, status, build_dir):
        # 获取构建类型
        build_type = self.params.get('build_type', 'Release')
        if code != 0:
            self.log_output.append(f"构建失败，返回码：{code}")
            return
        self.log_output.append("构建完成，开始运行...")
        # 查找并运行 exe
        alg = self.combo_alg.currentText()
        exe_base = alg.split("_",1)[1] if "_" in alg else alg
        exe_name = exe_base + (".exe" if sys.platform.startswith("win") else "")
        # 查找路径
        candidate = [os.path.join(build_dir, exe_name)]
        if not os.path.exists(candidate[0]):
            candidate.insert(0, os.path.join(build_dir, build_type, exe_name))
        exe_path = next((p for p in candidate if os.path.exists(p)), None)
        if exe_path:
            # 在独立的 cmd 窗口中使用 start 启动可执行文件
            QProcess.startDetached("cmd.exe", ["/C", "start", "", exe_path])
            # 打开可执行文件所在目录
            exe_dir = os.path.dirname(exe_path)
            QProcess.startDetached("explorer", [exe_dir])
        else:
            self.log_output.append("未找到可执行文件，运行失败。")

    def run_process(self, cmd, cwd):
        process = QProcess(self)
        process.setWorkingDirectory(cwd)
        process.readyReadStandardOutput.connect(lambda: self.handle_output(process, False))
        process.readyReadStandardError.connect(lambda: self.handle_output(process, True))
        process.finished.connect(lambda code, status: self.log_output.append(f"进程结束，返回码：{code}"))
        process.start(cmd[0], cmd[1:])

    def handle_output(self, process, is_err):
        # 读取原始字节数据
        raw = process.readAllStandardError().data() if is_err else process.readAllStandardOutput().data()
        # 优先尝试 UTF-8 解码，失败后降级到 GBK
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('gbk', errors='replace')
        # 将解码后的文本追加到日志
        self.log_output.append(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 应用科技风暗色主题
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = MainWindow()
    win.show()
    sys.exit(app.exec()) 