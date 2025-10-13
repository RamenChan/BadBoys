#Basit Hesap Makinesi Uygulaması ( Terminalde )

result = "0"
number = ""
number1 = ""
calculationType = ""

def CalculatorView():
    print("=" * 49)
    print("|", " " * (44 - len(str(result))), result, "|")
    print("=" * 49)
    print("|", " " * 2, "AC", " " * 3, "|", " ", "(+/-)", " ", "|", " " * 3, "%", " " * 3, "|", " " * 3, "/", " " * 3, "|")
    print("=" * 49)
    print("|", " " * 3, "7", " " * 3, "|", " " * 3, "8", " " * 3, "|", " " * 3, "9", " " * 3, "|", " " * 3, "X", " " * 3, "|")
    print("=" * 49)
    print("|", " " * 3, "4", " " * 3, "|", " " * 3, "5", " " * 3, "|", " " * 3, "6", " " * 3, "|", " " * 3, "-", " " * 3, "|")
    print("=" * 49)
    print("|", " " * 3, "1", " " * 3, "|", " " * 3, "2", " " * 3, "|", " " * 3, "3", " " * 3, "|", " " * 3, "+", " " * 3, "|")
    print("=" * 49)
    print("|", " " * 3, "U", " " * 3, "|", " " * 3, "0", " " * 3, "|", " " * 3, ",", " " * 3, "|", " " * 3, "=", " " * 3, "|")
    print("=" * 49)
    if int(result) !=0 and int(number) != 0 and int(number1) != 0:
        Calculation()
    else:
        FirstCalculation()


def Calculation():
    global number
    global number1
    global result

    number = result
    calculationType = input()
    number1 = input()
    if calculationType == "AC" or number1 == "AC":
        result = "0"
        CalculatorView()
    else:
        CalculatorOperastions(calculationType)

def FirstCalculation():
    global number
    global number1
    global result

    number = input()
    calculationType = input()
    number1 = input()
    if calculationType == "AC" or number1 == "AC" or number == "AC":
        result = "0"
        CalculatorView()
    else:
        CalculatorOperastions(calculationType)


def CalculatorOperastions(calculationType):
    global result

    match calculationType:
        case "+":
            result = int(number) + int(number1)
            CalculatorView()
        case "-":
            result = int(number) - int(number1)
            CalculatorView()
        case "*":
            result = int(number) * int(number1)
            CalculatorView()
        case "/":
            result = int(number) / int(number1)
            CalculatorView()
        case "%":
            result = int(number) % int(number1)
            CalculatorView()

CalculatorView()