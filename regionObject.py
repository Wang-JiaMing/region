class regionObject:
    '所有员工的基类'
    empCount = 0
    id=0;
    string
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        regionObject.empCount += 1

    def displayCount(self):
        print("Total Employee %d" % regionObject.empCount)

    def displayEmployee(self):
        print("Name : ", self.name, ", Salary: ", self.salary)


"创建 Employee 类的第一个对象"
emp1 = regionObject("Zara", 2000)
"创建 Employee 类的第二个对象"
emp2 = regionObject("Manni", 5000)
emp1.displayEmployee()
emp2.displayEmployee()
print("Total Employee %d" % regionObject.empCount)
