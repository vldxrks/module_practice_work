#include <iostream>
#include <vector>
#include <cmath> // Для M_PI та pow()

// Базовий клас
class RotationFigure {
public:
    virtual void printData() {
        std::cout << "Це абстрактна фігура обертання." << std::endl;
    }
    
    // Віртуальний деструктор для безпечного видалення через указівник
    virtual ~RotationFigure() {}
};

// Похідний клас
class Cone : public RotationFigure {
private:
    double radius;
    double height;

public:
    Cone(double r, double h) : radius(r), height(h) {}

    void printData() override {
        // Формула об'єму конуса: V = (1/3) * π * r^2 * h
        double volume = (1.0 / 3.0) * M_PI * std::pow(radius, 2) * height;
        std::cout << "Конус: радіус = " << radius 
                  << ", висота = " << height 
                  << ", об'єм = " << volume << std::endl;
    }
};

int main() {
    // Створюємо масив указівників на базовий клас
    const int size = 2;
    RotationFigure* figures[size];

    // Заповнюємо масив різними типами об'єктів
    figures[0] = new RotationFigure();
    figures[1] = new Cone(5.0, 12.0); // Радіус 5, висота 12

    std::cout << "--- Дані про фігури ---" << std::endl;

    // Виводимо дані в циклі (поліморфізм у дії)
    for (int i = 0; i < size; i++) {
        figures[i]->printData();
    }

    // Очищення пам'яті
    for (int i = 0; i < size; i++) {
        delete figures[i];
    }

    return 0;
}