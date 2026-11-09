import cv2

class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        s = self.height / 100
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)

        text_x = self.pos[0] + self.width // 2 - int(15 * s)
        text_y = self.pos[1] + self.height // 2 + int(15 * s)

        cv2.putText(img, self.value, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN,
                    3 * s, (50, 50, 50), max(1, round(3 * s)))


# MUST be configured for each system
cap = cv2.VideoCapture(0)

#input image size, based on your webcam
WIDTH = 1920
HEIGHT = 1080
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

success, img = cap.read()
if not success:
    print("Failed to read frame")
    exit(1)
HEIGHT, WIDTH = img.shape[:2]
scale = HEIGHT / 1080
size = int(100 * scale)

# basic list of buttons, may be changed (changes must be justified)
buttonListValues = [['C', '<'],
                    ['7', '8', '9', '/'],  # ÷ cant be rendered, so well have to do with / :/
                    ['4', '5', '6', '*'],
                    ['1', '2', '3', '-'],
                    ['0', '.', '=', '+']]

buttonlist = []
for y in range(5):
    for x in range(4):
        if y == 0 and x >= 2:  # first row only has 2 buttons (C and <), so kinda special case
            break

        xpos = int(WIDTH - 5 * size + x * size)
        ypos = int(HEIGHT * 0.15 + y * size)

        # first row special case, second button needs to be shifted
        if y == 0 and x == 1: #not the most elegant
            xpos += size

        if y == 0:
            width = 2 * size
            buttonlist.append(Button((xpos, ypos), width, size, buttonListValues[y][x]))
        else:
            buttonlist.append(Button((xpos, ypos), size, size, buttonListValues[y][x]))

operation = ""

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read frame")
        break

    operation_x = int(WIDTH - 5 * size)
    operation_y = int(HEIGHT * 0.05)

    cv2.rectangle(img, (operation_x, operation_y), (operation_x + 4 * size, operation_y + int(1.2 * size)),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (operation_x, operation_y), (operation_x + 4 * size, operation_y + int(1.2 * size)),
                  (50, 50, 50), 3)

    for button in buttonlist:
        button.draw(img)

    # when something triggers, the calculator should actually calculate
    # the something should be programmed by you, of course
    something = False
    received_val = ""
    if something:
        if received_val == "=":
            try:
                operation = str(eval(operation))
            except:
                operation = "Error"
        elif received_val == "C":  # Reset
            operation = ""
        elif received_val == "<":  # remove char
            operation = operation[:-1]
        else:
            operation += received_val
        delayCounter = 1

    cv2.putText(img, operation, (operation_x + int(0.1 * size), operation_y + int(0.75 * size)),
                cv2.FONT_HERSHEY_PLAIN, 3 * scale, (50, 50, 50), max(1, round(3 * scale)))

    cv2.imshow('Calculator', img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

