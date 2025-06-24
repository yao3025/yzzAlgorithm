import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QTextEdit
)
from PySide6.QtCore import QProcess
import qdarkstyle

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("算法管理程序")  # 窗口标题
        self.resize(800, 600)
        self.setup_ui()
        self.populate_algorithms()

    def setup_ui(self):
        # 顶部布局：算法选择、CMake 参数、按钮
        label_alg = QLabel("算法：")
        self.combo_alg = QComboBox()
        label_params = QLabel("CMake 参数：")
        self.edit_params = QLineEdit("-DCMAKE_BUILD_TYPE=Release")
        self.btn_build = QPushButton("编译并运行")

        top_layout = QHBoxLayout()
        top_layout.addWidget(label_alg)
        top_layout.addWidget(self.combo_alg)
        top_layout.addWidget(label_params)
        top_layout.addWidget(self.edit_params)
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
        self.btn_build.clicked.connect(self.on_build)

    def populate_algorithms(self):
        # 项目根目录，两级上
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        for name in os.listdir(root):
            path = os.path.join(root, name)
            # 目录名以序号_算法名格式
            if os.path.isdir(path) and name and name[0].isdigit() and "_" in name:
                self.combo_alg.addItem(name)

    def on_build(self):
        alg = self.combo_alg.currentText()
        params = self.edit_params.text().split()
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        alg_dir = os.path.join(root, alg)
        build_dir = os.path.join(alg_dir, "build")
        # 创建 build 目录
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        # 配置
        self.log_output.append(f"正在配置：{alg} ...")
        cfg_cmd = ["cmake", alg_dir] + params
        self.run_process(cfg_cmd, build_dir)

        # 编译
        self.log_output.append(f"正在编译：{alg} ...")
        build_cmd = ["cmake", "--build", "."]
        self.run_process(build_cmd, build_dir)

        # 运行
        exe_name = alg + (".exe" if sys.platform.startswith("win") else "")
        exe_path = os.path.join(build_dir, exe_name)
        if os.path.exists(exe_path):
            self.log_output.append(f"正在运行：{exe_path} ...")
            self.run_process([exe_path], build_dir)
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
        data = process.readAllStandardError().data().decode('utf-8') if is_err else process.readAllStandardOutput().data().decode('utf-8')
        self.log_output.append(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 应用科技风暗色主题
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = MainWindow()
    win.show()
    sys.exit(app.exec()) 