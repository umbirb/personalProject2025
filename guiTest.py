import customtkinter as ctk
from PIL import Image, ImageTk

# Set appearance and theme
ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Create main window
root = ctk.CTk()
root.geometry("500x400")
root.title("CustomTkinter Demo")

# Create a frame
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

def loadImage(imageFile):
    '''
    This function loads an image from a file and returns a PhotoImage object
    '''
    image=Image.open(imageFile)
    image = image.resize((100, 120))
    photo=ImageTk.PhotoImage(image)
    return photo

def loadText(textFile):
    '''
    This function loads text from a file and returns a string
    '''
    with open(textFile, "r") as file:
        text = file.read()
    return text 


# ---- add the questions ----

question_index = 0
# show a button to go to the next question
def screen1():
    global question_index
    print("Next question")
    # update the image
    photo2 = loadImage("image2.png")
    label2.configure(image=photo2) 
    # update the text
    text2 = loadText("text1.txt")
    label3.configure(text=text2)
    if question_index >= 0:
        button.configure(text=f" Index {question_index} ..Next")
        question_index += 1
        

# create the widgets for the screen
# Title
label1 = ctk.CTkLabel(master=frame, text="Quiz Master", font=("Arial", 26))
label1.pack(pady=10)

# display image and make it clickable
def on_image_click(event):
    print("Image clicked!")

photo1 = loadImage("image.png")
label2 = ctk.CTkLabel(master=frame, image=photo1, text="")  # note you have to set empty text to display the image
label2.pack(pady=10)
#label2.bind("<Button-1>", on_image_click)  # bind left mouse button click event to the image

# display text with wrap
text1 = loadText("text2.txt")
label3 = ctk.CTkLabel(master=frame, text=text1, font=("Arial", 12), wraplength=400, anchor="w", justify="left")
label3.pack(pady=10)

# Button
button = ctk.CTkButton(master=frame, text="Begin", command=screen1)
button.pack(pady=10)

# Run the application
root.mainloop()
