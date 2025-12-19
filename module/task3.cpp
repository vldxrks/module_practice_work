#include <iostream>

// Завдання 3: Шаблонна функція пошуку в діапазоні
template <typename T>
void searchInRange(T arr[], int size, T minVal, T maxVal) {
    std::cout << "Елементи в діапазоні [" << minVal << ", " << maxVal << "]: ";
    for (int i = 0; i < size; i++) {
        if (arr[i] >= minVal && arr[i] <= maxVal) {
            std::cout << arr[i] << " ";
        }
    }
    std::cout << std::endl;
}

// Завдання 4: Шаблон класу для пари різних типів
template <typename T1, typename T2>
class Pair {
    T1 first;
    T2 second;
public:
    Pair(T1 f, T2 s) : first(f), second(s) {}
    void display() {
        std::cout << "Пара значень: " << first << " та " << second << std::endl;
    }
};

int main() {
    // Тест шаблону функції
    int iArr[] = {1, 5, 12, 18, 25};
    searchInRange(iArr, 5, 10, 20);

    double dArr[] = {1.1, 2.5, 3.8, 5.9};
    searchInRange(dArr, 4, 2.0, 4.5);

    std::cout << "------------------------" << std::endl;

    // Тест шаблону класу
    Pair<int, double> p1(10, 3.14);
    p1.display();

    Pair<std::string, int> p2("Вік", 20);
    p2.display();

    return 0;
}