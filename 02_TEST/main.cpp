#include <iostream>
#ifdef _WIN32
#include <windows.h>
#endif

// KMP 算法示例主函数
int main() {
    #ifdef _WIN32
        // 设置控制台为 UTF-8 编码
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
    #endif
    std::cout << u8"KMP 算法示例" << std::endl;
    //  运行暂停
    std::cout << "按回车键继续..." << std::endl;
    std::cin.get();
    return 0;
} 