#for loop - არის ციკლი, რომლის მეშვეობითაც შეგვიძლია გარკვეული დავალების შესრულების განმავლობაში ან გარკვეული პირობის შესრულების განმავლობაში გარკვეული დავალება გავაკეთებინოთ
#indendation - არის 4 space. ის აუცილებელია, რადგან for loop-ში ჩაწერილი პროგრამა აუცილებლად უნდა იყოს ამ წესით ჩასმული
for i in range(68):
    print(i)

for i in range(12, 88):
    print(i)

for i in range(4, 99, 2):
    print(i)

for i in range(10):
    print("Andria")

word = input("Enter your word:")

for letter in word:
    print(letter)

num = int(input("Enter your number:"))

for i in range(num + 1):
    print(i)