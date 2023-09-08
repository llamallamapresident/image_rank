import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from functions import load_elo_ratings, sort_dict_by_scores, save_elo_ratings, caculate_rating, loading_conflict, images_in_folder, images_in_csv
from imagefunctions import resize_image
import os
import csv
import shutil

class ImageCompareMetadata:
    def __init__(self, folder_path, csv_path, reset_csv, cycles_n):
        self.folder_path = folder_path
        self.csv_path = csv_path
        self.reset_csv = reset_csv
        self.cycles_n = cycles_n

class ImageCompareWindow:
    def __init__(self, root, metadata):
        self.root = root
        self.root.title("Image Compare Window")
        self.root.focus_set()

        self.image_folder = metadata.folder_path
        self.csv_path = metadata.csv_path
        self.elo_ratings = load_elo_ratings(self.image_folder, self.csv_path, new_csv=metadata.reset_csv)
        self.ordered_image_list = list(self.elo_ratings.keys())

        self.current_index = 0
        self.total_indexes = len(self.elo_ratings)
        self.current_cycle = 0
        self.total_cycles = metadata.cycles_n

        self.resize_width = 500
        self.resize_height = 500

        self.left_image_label = tk.Label(root, width=self.resize_width, height=self.resize_height)
        self.left_image_label.grid(row=0, column=0, padx=10, pady=10)
        self.left_image_label.bind("<Button-1>", self.left_win)
        self.left_image_text = tk.Label(root, text="", font=("Helvetica", 16))
        self.left_image_text.grid(row=1, column=0, padx=10, pady=10)
        self.root.bind("<a>", self.left_win)

        self.counter_label = tk.Label(root, height=3, text="", font=("Helvetica", 14))
        self.counter_label.grid(row=2, column=1, padx=10, pady=10)

        self.right_image_label = tk.Label(root, width=self.resize_width, height=self.resize_height)
        self.right_image_label.grid(row=0, column=2, padx=10, pady=10)
        self.right_image_label.bind("<Button-1>", self.right_win)
        self.right_image_text = tk.Label(root, text="", font=("Helvetica", 16))
        self.right_image_text.grid(row=1, column=2, padx=10, pady=10)
        self.root.bind("<d>", self.right_win)

        self.draw_button = tk.Button(root, text="Draw\nKey binding:\"s\"", command=self.draw, width=15, height=3)
        self.draw_button.grid(row=0, column=1, padx=10, pady=10)
        self.root.bind("<s>", self.draw)

        self.show_images()

    def show_images(self, final_image=False):
        
        # Get image
        left_image_name = self.ordered_image_list[self.current_index]
        if final_image:
            right_image_name = self.ordered_image_list[self.current_index - 1]
        else:
            right_image_name = self.ordered_image_list[self.current_index + 1]
        left_image_path = os.path.join(self.image_folder, left_image_name)
        right_image_path = os.path.join(self.image_folder, right_image_name)

        # Update images
        left_image = Image.open(left_image_path)
        left_image = resize_image(left_image, self.resize_width, self.resize_height)
        self.left_photo = ImageTk.PhotoImage(left_image)
        self.left_image_label.config(image=self.left_photo)

        right_image = Image.open(right_image_path)
        right_image = resize_image(right_image, self.resize_width, self.resize_height)
        self.right_photo = ImageTk.PhotoImage(right_image)
        self.right_image_label.config(image=self.right_photo)

        # Update text
        if len(left_image_name) <= 25:
            left_text_string = f"Image name:{left_image_name}\nElo:{self.elo_ratings[left_image_name]}\nKey binding:\"a\""
        else:
            left_text_string = f"Image name:{left_image_name[:23]}...\nElo:{self.elo_ratings[left_image_name]}\nKey binding:\"a\""
        self.left_image_text.config(text=left_text_string)
        if len(right_image_name) <= 25:
            right_text_string = f"Image name:{right_image_name}\nElo:{self.elo_ratings[right_image_name]}\nKey binding:\"d\""
        else:
            right_text_string = f"Image name:{right_image_name[:23]}...\nElo:{self.elo_ratings[right_image_name]}\nKey binding:\"d\""
        self.right_image_text.config(text=right_text_string)

        # Update counter
        self.counter_label.config(text=f"{self.current_index} out of {self.total_indexes} images\n{self.current_cycle} out of {self.total_cycles} cycles")

    def left_win(self, event=None):
        self.update_elos(outcome=1)
        self.show_next_images()

    def right_win(self, event=None):
        self.update_elos(outcome=0)
        self.show_next_images()

    def draw(self, event=None):
        self.update_elos(outcome=0.5)
        self.show_next_images()

    def update_elos(self, outcome=0.5):
        """
        1 if left win, 0 if right win, 0.5 if draw
        """
        left_image = self.ordered_image_list[self.current_index]
        left_elo = self.elo_ratings[left_image]
        if self.current_index + 1 < self.total_indexes:
            right_image = self.ordered_image_list[self.current_index + 1]
            right_elo = self.elo_ratings[right_image]
        else:
            right_image = self.ordered_image_list[self.current_index - 1]
            right_elo = self.elo_ratings[right_image]

        new_left_elo = caculate_rating(player_rating=left_elo, opponent_rating=right_elo, result=outcome)
        new_right_elo = caculate_rating(player_rating=right_elo, opponent_rating=left_elo, result=1-outcome)
        self.elo_ratings[left_image] = new_left_elo
        self.elo_ratings[right_image] = new_right_elo
    
    def show_next_images(self):
        self.current_index += 1

        if self.current_index >= self.total_indexes:
            self.next_cycle()
        elif self.current_index + 1 >= self.total_indexes:
            self.show_images(final_image=True)
        else:
            self.show_images()

    def next_cycle(self):
        self.elo_ratings = sort_dict_by_scores(self.elo_ratings)
        self.ordered_image_list = list(self.elo_ratings.keys())

        save_elo_ratings(self.csv_path, self.elo_ratings)

        self.current_cycle += 1
        if self.current_cycle >= self.total_cycles:
            self.root.destroy()
            return

        self.current_index = 0
        self.show_images()

class ImageCompareApp:
    def __init__(self, root, menu_root):
        self.root = root
        self.root.title("Image Compare App")
        self.root.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.menu_root = menu_root
        
        self.create_savedata_folder()
        self.current_dir = os.getcwd()

        # Folder input entry
        self.label_folder_path = tk.Label(self.root, text="Folder Path:")
        self.label_folder_path.pack()
        self.entry_folder_path = tk.Entry(self.root, width=70)
        self.entry_folder_path.pack()

        # Folder input browser
        self.button_browse_folder = tk.Button(self.root, text="Browse Folder", command=self.browse_folder)
        self.button_browse_folder.pack()
        self.label_folder_count = tk.Label(self.root, text="Images in folder = ", width=30)
        self.label_folder_count.pack()

        # CSV input entry
        self.label_csv_path = tk.Label(self.root, text="CSV Path:")
        self.label_csv_path.pack()
        self.entry_csv_path = tk.Entry(self.root, width=70)
        self.entry_csv_path.pack()

        # CSV input browser and options
        self.button_browse_csv = tk.Button(self.root, text="Browse CSV", command=self.browse_csv)
        self.button_browse_csv.pack()
        self.button_create_csv = tk.Button(self.root, text="Create a new CSV", command=self.create_csv)
        self.button_create_csv.pack()
        self.label_csv_count = tk.Label(self.root, text="Images in CSV = \nMax elo = \nMin elo = ", width=30)
        self.label_csv_count.pack()
        self.reset_csv_var = tk.BooleanVar()
        self.reset_csv_checkbox = tk.Checkbutton(self.root, text="Reset CSV", variable=self.reset_csv_var)
        self.reset_csv_checkbox.pack()

        # Check for mismatch in folder and CSV
        self.label_files_match = tk.Label(self.root, text="", width=30)
        self.label_files_match.pack()

        # Cycles input
        self.label_cycles = tk.Label(self.root, text="Number of cycles:")
        self.label_cycles.pack()
        self.cycle_var = tk.IntVar()
        self.cycle_var.set(1)
        self.entry_cycles = tk.Spinbox(root, from_=1, to=100, textvariable=self.cycle_var)
        self.entry_cycles.pack()

        # Start button
        self.button_start = tk.Button(self.root, text="Start", command=self.start)
        self.button_start.pack()

        # Back button
        self.button_back = tk.Button(self.root, text="Back", command=self.back)
        self.button_back.pack()

    def create_savedata_folder(self):
        # Create a folder called "savedata" if it doesn't exist
        if not os.path.exists("savedata"):
            os.makedirs("savedata")

    def browse_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_dir, title="Select a Folder")
        self.entry_folder_path.delete(0, tk.END)
        self.entry_folder_path.insert(0, folder_path)
        self.update_selection_info()

    def browse_csv(self):
        file_path = filedialog.askopenfilename(initialdir="savedata/", filetypes=[("CSV Files", "*.csv")])
        self.entry_csv_path.delete(0, tk.END)
        self.entry_csv_path.insert(0, file_path)
        self.update_selection_info()

    def create_csv(self):
        file_path = filedialog.asksaveasfilename(initialdir="savedata/", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])

        with open(file_path, mode='w', newline='') as csvfile:
            fieldnames = ["image_name", "elo"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        self.entry_csv_path.delete(0, tk.END)
        self.entry_csv_path.insert(0, file_path)
        self.update_selection_info()

    def update_selection_info(self):
        folder_path = self.entry_folder_path.get()
        csv_path = self.entry_csv_path.get()
        folder_path_valid = True
        csv_path_valid = True

        # Validate paths
        if folder_path == "":
            self.label_folder_count.config(text="Images in folder = ")
            folder_path_valid = False
        elif not os.path.exists(folder_path):
            self.label_folder_count.config(text="Invalid folder path")
            folder_path_valid = False

        if csv_path == "":
            self.label_csv_count.config(text="Images in CSV = \nMax elo = \nMin elo = ")
            csv_path_valid = False
        elif not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            self.label_csv_count.config(text="Invalid CSV file")
            csv_path_valid = False

        # Display info on folder path
        if folder_path_valid:
            folder_files_n = len(images_in_folder(folder_path))
            self.label_folder_count.config(text=f"Images in folder = {folder_files_n}")

        # Display info on csv path
        if csv_path_valid:
            csv_files_n = len(images_in_csv(csv_path))
            min_elo = 10000.0
            max_elo = 0.0
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if float(row["elo"]) > max_elo:
                        max_elo = float(row["elo"])
                    if float(row["elo"]) < min_elo:
                        min_elo = float(row["elo"])
            self.label_csv_count.config(text=f"Images in CSV = {csv_files_n}\nMax elo = {max_elo}\nMin elo = {min_elo}")

        # Display info on both folder path and csv path
        if folder_path_valid and csv_path_valid:
            loading_conflict_folder = loading_conflict(folder_path, csv_path, in_csv=False)
            loading_conflict_csv = loading_conflict(folder_path, csv_path, in_csv=True)
            self.label_files_match.config(text=f"Missing from folder: {loading_conflict_csv}\nMissing from CSV: {loading_conflict_folder}")

    def start(self):
        folder_path = self.entry_folder_path.get()
        csv_path = self.entry_csv_path.get()
        reset_csv = self.reset_csv_var.get()
        cycles_n = self.entry_cycles.get()

        # Check all values are valid
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Invalid folder path")
            return
        if not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            messagebox.showerror("Error", "Invalid CSV file")
            return
        try:
            cycles_n = int(cycles_n)
            if cycles_n <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid number of cycles")
            return
        
        # Check if there are missing images in the folder compared to the csv and ask the user if they wish to continue
        missing_images_n = loading_conflict(folder_path, csv_path, in_csv=True)
        if missing_images_n == 0:
            metadata = ImageCompareMetadata(folder_path, csv_path, reset_csv, cycles_n)
            self.image_compare_child = tk.Toplevel(self.root)
            image_compare_window = ImageCompareWindow(self.image_compare_child, metadata)
        else:
            user_response = messagebox.askquestion("Warning", f"{missing_images_n} filenames in csv not present in folder.\
                                                   Do you wish to delete {missing_images_n} items from the csv?")
            if user_response == "yes":
                metadata = ImageCompareMetadata(folder_path, csv_path, reset_csv, cycles_n)
                self.image_compare_child = tk.Toplevel(self.root)
                image_compare_window = ImageCompareWindow(self.image_compare_child, metadata)
            else:
                return
            
    def back(self):
        self.menu_root.deiconify()
        self.root.destroy()

    def close(self):
        self.menu_root.destroy()

class ImageDisplayMetadata:
    def __init__(self, folder_path, csv_path, display_n, sort_order):
        self.folder_path = folder_path
        self.csv_path = csv_path
        self.display_n = display_n
        self.sort_order = sort_order

class ImageDisplayWindow:
    def __init__(self, root, metadata):
        self.root = root
        self.root.title("Image Display Window")
        self.root.focus_set()

        self.image_folder = metadata.folder_path
        self.csv_path = metadata.csv_path
        self.current_dir = os.getcwd()

        self.elo_ratings = load_elo_ratings(self.image_folder, self.csv_path, new_csv=False)
        # Order the iamges acordingly
        if metadata.sort_order == "Elo ascending":
            self.elo_ratings = sort_dict_by_scores(self.elo_ratings, reverse=False)
        elif metadata.sort_order == "Elo descending":
            self.elo_ratings = sort_dict_by_scores(self.elo_ratings, reverse=True)
        else:
            raise Exception("Invalid sort order")
        self.ordered_image_list = list(self.elo_ratings.keys())

        self.current_index = 0
        self.total_indexes = metadata.display_n
        if self.total_indexes == 0 or self.total_indexes > len(self.ordered_image_list):
            self.total_indexes = len(self.ordered_image_list)
        self.delete_list = []
        self.move_list = [] #(filename, destination dir)

        self.resize_width = 600
        self.resize_height = 600

        self.image_label = tk.Label(root, width=self.resize_width, height=self.resize_height)
        self.image_label.grid(row=0, column=0, padx=10, pady=10)
        self.image_label.bind("<Button-1>", self.pass_image)
        self.image_text = tk.Label(root, text="", font=("Helvetica", 16))
        self.image_text.grid(row=1, column=0, padx=10, pady=10)
        self.root.bind("<KeyPress-space>", self.pass_image)

        self.counter_label = tk.Label(root, height=3, text="", font=("Helvetica", 14))
        self.counter_label.grid(row=2, column=0, padx=10, pady=10)

        self.back_button = tk.Button(root, text="Back\nKey binding:\"a\"", command=self.back, width=15, height=3)
        self.back_button.grid(row=0, column=1, padx=10, pady=10)
        self.root.bind("<a>", self.back)

        self.move_button = tk.Button(root, text="Move\nKey binding:\"s\"", command=self.move, width=15, height=3)
        self.move_button.grid(row=1, column=1, padx=10, pady=10)
        self.root.bind("<s>", self.move)

        self.delete_button = tk.Button(root, text="Delete\nKey binding:\"d\"", command=self.delete, width=15, height=3)
        self.delete_button.grid(row=2, column=1, padx=10, pady=10)
        self.root.bind("<d>", self.delete)

        self.show_images()

    def show_images(self):
        
        # Get image
        image_name = self.ordered_image_list[self.current_index]
        image_path = os.path.join(self.image_folder, image_name)

        # Update images
        image = Image.open(image_path)
        image = resize_image(image, self.resize_width, self.resize_height)
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.photo)

        # Update text
        if len(image_name) <= 25:
            text_string = f"Image name:{image_name}\nElo:{self.elo_ratings[image_name]}\nKey binding:\"Spacebar\""
        else:
            text_string = f"Image name:{image_name[:23]}...\nElo:{self.elo_ratings[image_name]}\nKey binding:\"Spacebar\""
        self.image_text.config(text=text_string)

        # Update counter
        self.counter_label.config(text=f"{self.current_index} out of {self.total_indexes} images")

    def pass_image(self, event=None):
        self.show_next_images(1)

    def back(self, event=None):
        # Remove the previous index from the delete and move lists
        previous_index = self.current_index - 1
        if previous_index < 0:
            previous_index = 0
        if previous_index in self.delete_list:
            self.delete_list.remove(previous_index)
        self.move_list = [tup for tup in self.move_list if tup[0] != previous_index]
        self.show_next_images(-1)

    def move(self, event=None):
        destination_path = filedialog.askdirectory(initialdir=self.current_dir, title="Select a Folder")
        if destination_path == "":
            return
        self.move_list.append((self.current_index, destination_path))
        self.root.focus_set()
        self.show_next_images(1)
    
    def delete(self, event=None):
        self.delete_list.append(self.current_index)
        self.show_next_images(1)

    def show_next_images(self, index_change):
        self.current_index = self.current_index + index_change
        if self.current_index < 0:
            self.current_index = 0
        if self.current_index >= self.total_indexes:
            self.end()
            return
        self.show_images()

    def end(self):
        # Move all files on delete_list to recycle bin, move all files on move_list to selected folder, and close the window
        for index in self.delete_list:
            filename = self.ordered_image_list[index]
            file_path = os.path.join(self.image_folder, filename)
            destination_folder = os.path.join(self.current_dir, "recycle_bin")

            # Choose what to do with dupes, weather replace or skip
            if os.path.exists(os.path.join(destination_folder, filename)):
                user_response = messagebox.askquestion("Warning", f"{filename} present in recycle bin.\
                                                    Do you wish to replace {filename} from the recycle bin?")
                if user_response == "yes":
                    os.remove(os.path.join(destination_folder, filename))
                else:
                    continue
            shutil.move(file_path, destination_folder)

        for index, destination_folder in self.move_list:
            filename = self.ordered_image_list[index]
            file_path = os.path.join(self.image_folder, filename)

            # Choose what to do with dupes, weather replace or skip
            if os.path.exists(os.path.join(destination_folder, filename)):
                user_response = messagebox.askquestion("Warning", f"{filename} present in {destination_folder}.\
                                                    Do you wish to replace {filename} from the {destination_folder}?")
                if user_response == "yes":
                    os.remove(os.path.join(destination_folder, filename))
                else:
                    continue

            shutil.move(file_path, destination_folder)
        
        self.root.destroy()
        return

class ImageDisplayApp:
    def __init__(self, root, menu_root):
        self.root = root
        self.root.title("Image Display App")
        self.root.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.menu_root = menu_root
        
        self.create_savedata_folder()
        self.create_recyclebin_folder()
        self.current_dir = os.getcwd()

        # Folder input entry
        self.label_folder_path = tk.Label(self.root, text="Folder Path:")
        self.label_folder_path.pack()
        self.entry_folder_path = tk.Entry(self.root, width=70)
        self.entry_folder_path.pack()
        self.button_browse_folder = tk.Button(self.root, text="Browse Folder", command=self.browse_folder)
        self.button_browse_folder.pack()
        self.label_folder_count = tk.Label(self.root, text="Images in folder = ", width=30)
        self.label_folder_count.pack()

        # CSV input entry
        self.label_csv_path = tk.Label(self.root, text="CSV Path:")
        self.label_csv_path.pack()
        self.entry_csv_path = tk.Entry(self.root, width=70)
        self.entry_csv_path.pack()
        self.button_browse_csv = tk.Button(self.root, text="Browse CSV", command=self.browse_csv)
        self.button_browse_csv.pack()
        self.label_csv_count = tk.Label(self.root, text="Images in CSV = \nMax elo = \nMin elo = ", width=30)
        self.label_csv_count.pack()

        # Check for mismatch in folder and CSV
        self.label_files_match = tk.Label(self.root, text="", width=30)
        self.label_files_match.pack()

        # Select number of images to display
        self.label_display_n = tk.Label(self.root, text="Number of images to display (0 to show all):")
        self.label_display_n.pack()
        self.display_n_var = tk.IntVar()
        self.display_n_var.set(0)
        self.entry_display_n = tk.Spinbox(root, from_=0, to=10, textvariable=self.display_n_var)
        self.entry_display_n.pack()

        # Select sorting order
        self.label_sort_order = tk.Label(self.root, text="Sorting options:")
        self.label_sort_order.pack()
        self.sort_order_list = ["Elo ascending", "Elo descending"]
        self.sort_order_var = tk.StringVar()
        self.sort_order_var.set("Elo ascending")
        self.entry_sort_order = ttk.Combobox(root, values=self.sort_order_list, textvariable=self.sort_order_var, state="readonly")
        self.entry_sort_order.pack()

        # Start button
        self.button_start = tk.Button(self.root, text="Start", command=self.start)
        self.button_start.pack()

        # Clear recycle bin button
        self.button_clear_recyclebin = tk.Button(self.root, text="Clear recycle bin", command=self.clear_recyclebin)
        self.button_clear_recyclebin.pack()

        # Back button
        self.button_back = tk.Button(self.root, text="Back", command=self.back)
        self.button_back.pack()

    def create_savedata_folder(self):
        if not os.path.exists("savedata"):
            os.makedirs("savedata")

    def create_recyclebin_folder(self):
        if not os.path.exists("recycle_bin"):
            os.makedirs("recycle_bin")

    def browse_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_dir, title="Select a Folder")
        self.entry_folder_path.delete(0, tk.END)
        self.entry_folder_path.insert(0, folder_path)
        self.update_selection_info()

    def browse_csv(self):
        file_path = filedialog.askopenfilename(initialdir="savedata/", filetypes=[("CSV Files", "*.csv")])
        self.entry_csv_path.delete(0, tk.END)
        self.entry_csv_path.insert(0, file_path)
        self.update_selection_info()

    def update_selection_info(self):
        folder_path = self.entry_folder_path.get()
        csv_path = self.entry_csv_path.get()
        folder_path_valid = True
        csv_path_valid = True

        # Validate paths
        if folder_path == "":
            self.label_folder_count.config(text="Images in folder = ")
            folder_path_valid = False
        elif not os.path.exists(folder_path):
            self.label_folder_count.config(text="Invalid folder path")
            folder_path_valid = False

        if csv_path == "":
            self.label_csv_count.config(text="Images in CSV = \nMax elo = \nMin elo = ")
            csv_path_valid = False
        elif not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            self.label_csv_count.config(text="Invalid CSV file")
            csv_path_valid = False

        # Display info on folder path
        if folder_path_valid:
            folder_files_n = len(images_in_folder(folder_path))
            self.label_folder_count.config(text=f"Images in folder = {folder_files_n}")

        # Display info on csv path
        if csv_path_valid:
            csv_files_n = len(images_in_csv(csv_path))
            min_elo = 10000.0
            max_elo = 0.0
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if float(row["elo"]) > max_elo:
                        max_elo = float(row["elo"])
                    if float(row["elo"]) < min_elo:
                        min_elo = float(row["elo"])
            self.label_csv_count.config(text=f"Images in CSV = {csv_files_n}\nMax elo = {max_elo}\nMin elo = {min_elo}")
            self.entry_display_n.config(to=csv_files_n)

        # Display info on both folder path and csv path
        if folder_path_valid and csv_path_valid:
            loading_conflict_folder = loading_conflict(folder_path, csv_path, in_csv=False)
            loading_conflict_csv = loading_conflict(folder_path, csv_path, in_csv=True)
            self.label_files_match.config(text=f"Missing from folder: {loading_conflict_csv}\nMissing from CSV: {loading_conflict_folder}")

    def start(self):
        folder_path = self.entry_folder_path.get()
        csv_path = self.entry_csv_path.get()
        display_n = self.display_n_var.get()
        sort_order = self.sort_order_var.get()

        # Check all values are valid
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Invalid folder path")
            return
        if not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            messagebox.showerror("Error", "Invalid CSV file")
            return
        try:
            display_n = int(display_n)
            if display_n < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid number of images displayed")
            return
        if sort_order not in self.sort_order_list:
            messagebox.showerror("Error", "Invalid sort order")
            return
        
        # Check if there are missing images in the folder compared to the csv and ask the user if they wish to continue
        missing_images_n = loading_conflict(folder_path, csv_path)
        if missing_images_n == 0:
            metadata = ImageDisplayMetadata(folder_path, csv_path, display_n, sort_order)
            self.image_display_child = tk.Toplevel(self.root)
            image_display_window = ImageDisplayWindow(self.image_display_child, metadata)
        else:
            user_response = messagebox.askquestion("Warning", f"{missing_images_n} filenames in csv not present in folder.\
                                                   Do you wish to delete {missing_images_n} items from the csv?")
            if user_response == "yes":
                metadata = ImageDisplayMetadata(folder_path, csv_path, display_n, sort_order)
                self.image_display_child = tk.Toplevel(self.root)
                image_display_window = ImageDisplayWindow(self.image_display_child, metadata)
            else:
                return
            
    def clear_recyclebin(self):
        recyclebin_path = os.path.join(self.current_dir, "recycle_bin")
        shutil.rmtree(recyclebin_path)
        self.create_recyclebin_folder()

    def back(self):
        self.menu_root.deiconify()
        self.root.destroy()

    def close(self):
        self.menu_root.destroy()

class ImageTransferApp:
    def __init__(self, root, menu_root):
        self.root = root
        self.root.title("Image Transfer App")
        self.root.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.menu_root = menu_root
        
        self.create_savedata_folder()
        self.create_recyclebin_folder()
        self.current_dir = os.getcwd()

        # Input folder entry
        self.label_input_folder_path = tk.Label(self.root, text="Input folder Path:")
        self.label_input_folder_path.pack()
        self.entry_input_folder_path = tk.Entry(self.root, width=70)
        self.entry_input_folder_path.pack()
        self.button_browse_input_folder = tk.Button(self.root, text="Browse Input folder", command=self.browse_input_folder)
        self.button_browse_input_folder.pack()
        self.label_folder_count = tk.Label(self.root, text="Images in folder = ", width=30)
        self.label_folder_count.pack()

        # Destination folder entry
        self.label_destination_folder_path = tk.Label(self.root, text="Destination folder Path:")
        self.label_destination_folder_path.pack()
        self.entry_destination_folder_path = tk.Entry(self.root, width=70)
        self.entry_destination_folder_path.pack()
        self.button_browse_destination_folder = tk.Button(self.root, text="Browse Destination folder", command=self.browse_destination_folder)
        self.button_browse_destination_folder.pack()

        # CSV input entry
        self.label_csv_path = tk.Label(self.root, text="CSV Path:")
        self.label_csv_path.pack()
        self.entry_csv_path = tk.Entry(self.root, width=70)
        self.entry_csv_path.pack()
        self.button_browse_csv = tk.Button(self.root, text="Browse CSV", command=self.browse_csv)
        self.button_browse_csv.pack()
        self.label_csv_count = tk.Label(self.root, text="Images in CSV = \nMax elo = \nMin elo = ", width=30)
        self.label_csv_count.pack()

        # Check for mismatch in folder and CSV
        self.label_files_match = tk.Label(self.root, text="", width=30)
        self.label_files_match.pack()

        # Select number of images to transfer
        self.label_transfer_n = tk.Label(self.root, text="Number of images to transfer (0 to show all):")
        self.label_transfer_n.pack()
        self.transfer_n_var = tk.IntVar()
        self.transfer_n_var.set(0)
        self.entry_transfer_n = tk.Spinbox(root, from_=0, to=10, textvariable=self.transfer_n_var)
        self.entry_transfer_n.pack()

        # Select sorting order
        self.label_sort_order = tk.Label(self.root, text="Sorting options:")
        self.label_sort_order.pack()
        self.sort_order_list = ["Elo ascending", "Elo descending"]
        self.sort_order_var = tk.StringVar()
        self.sort_order_var.set("Elo ascending")
        self.entry_sort_order = ttk.Combobox(root, values=self.sort_order_list, textvariable=self.sort_order_var, state="readonly")
        self.entry_sort_order.pack()

        # Start button
        self.button_start = tk.Button(self.root, text="Start", command=self.start)
        self.button_start.pack()

        # Clear recycle bin button
        self.button_clear_recyclebin = tk.Button(self.root, text="Clear recycle bin", command=self.clear_recyclebin)
        self.button_clear_recyclebin.pack()

        # Back button
        self.button_back = tk.Button(self.root, text="Back", command=self.back)
        self.button_back.pack()

    def create_savedata_folder(self):
        if not os.path.exists("savedata"):
            os.makedirs("savedata")

    def create_recyclebin_folder(self):
        if not os.path.exists("recycle_bin"):
            os.makedirs("recycle_bin")

    def browse_input_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_dir, title="Select an input folder")
        self.entry_input_folder_path.delete(0, tk.END)
        self.entry_input_folder_path.insert(0, folder_path)
        self.update_selection_info()

    def browse_destination_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_dir, title="Select a destination folder")
        self.entry_destination_folder_path.delete(0, tk.END)
        self.entry_destination_folder_path.insert(0, folder_path)
        self.update_selection_info()

    def browse_csv(self):
        file_path = filedialog.askopenfilename(initialdir="savedata/", filetypes=[("CSV Files", "*.csv")])
        self.entry_csv_path.delete(0, tk.END)
        self.entry_csv_path.insert(0, file_path)
        self.update_selection_info()

    def update_selection_info(self):
        folder_path = self.entry_input_folder_path.get()
        csv_path = self.entry_csv_path.get()
        folder_path_valid = True
        csv_path_valid = True

        # Validate paths
        if folder_path == "":
            self.label_folder_count.config(text="Images in folder = ")
            folder_path_valid = False
        elif not os.path.exists(folder_path):
            self.label_folder_count.config(text="Invalid folder path")
            folder_path_valid = False

        if csv_path == "":
            self.label_csv_count.config(text="Images in CSV = \nMax elo = \nMin elo = ")
            csv_path_valid = False
        elif not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            self.label_csv_count.config(text="Invalid CSV file")
            csv_path_valid = False

        # Display info on folder path
        if folder_path_valid:
            folder_files_n = len(images_in_folder(folder_path))
            self.label_folder_count.config(text=f"Images in folder = {folder_files_n}")

        # Display info on csv path
        if csv_path_valid:
            csv_files_n = len(images_in_csv(csv_path))
            min_elo = 10000.0
            max_elo = 0.0
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if float(row["elo"]) > max_elo:
                        max_elo = float(row["elo"])
                    if float(row["elo"]) < min_elo:
                        min_elo = float(row["elo"])
            self.label_csv_count.config(text=f"Images in CSV = {csv_files_n}\nMax elo = {max_elo}\nMin elo = {min_elo}")
            self.entry_transfer_n.config(to=csv_files_n)

        # Display info on both folder path and csv path
        if folder_path_valid and csv_path_valid:
            loading_conflict_folder = loading_conflict(folder_path, csv_path, in_csv=False)
            loading_conflict_csv = loading_conflict(folder_path, csv_path, in_csv=True)
            self.label_files_match.config(text=f"Missing from folder: {loading_conflict_csv}\nMissing from CSV: {loading_conflict_folder}")

    def start(self):
        input_folder_path = self.entry_input_folder_path.get()
        destination_folder_path = self.entry_destination_folder_path.get()
        csv_path = self.entry_csv_path.get()
        transfer_n = self.transfer_n_var.get()
        sort_order = self.sort_order_var.get()

        # Check all values are valid
        if not os.path.exists(input_folder_path):
            messagebox.showerror("Error", "Invalid input folder path")
            return
        if not os.path.exists(destination_folder_path):
            messagebox.showerror("Error", "Invalid destination folder path")
            return
        if not os.path.isfile(csv_path) or not csv_path.endswith(".csv"):
            messagebox.showerror("Error", "Invalid CSV file")
            return
        try:
            transfer_n = int(transfer_n)
            if transfer_n < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid number of images displayed")
            return
        if sort_order not in self.sort_order_list:
            messagebox.showerror("Error", "Invalid sort order")
            return
        
        # Check if there are missing images in the folder compared to the csv and ask the user if they wish to continue
        missing_images_n = loading_conflict(input_folder_path, csv_path)
        if missing_images_n == 0:
            self.transfer_images()
        else:
            user_response = messagebox.askquestion("Warning", f"{missing_images_n} filenames in csv not present in folder.\
                                                   Do you wish to delete {missing_images_n} items from the csv?")
            if user_response == "yes":
                self.transfer_images()
            else:
                return
    
    def transfer_images(self):
        input_folder_path = self.entry_input_folder_path.get()
        destination_folder_path = self.entry_destination_folder_path.get()
        csv_path = self.entry_csv_path.get()
        transfer_n = int(self.transfer_n_var.get())
        sort_order = self.sort_order_var.get()
        skip_n = 0

        elo_ratings = load_elo_ratings(input_folder_path, csv_path, new_csv=False)
        # Order the iamges acordingly
        if sort_order == "Elo ascending":
            elo_ratings = sort_dict_by_scores(elo_ratings, reverse=False)
        elif sort_order == "Elo descending":
            elo_ratings = sort_dict_by_scores(elo_ratings, reverse=True)
        else:
            raise Exception("Invalid sort order")
        ordered_image_list = list(elo_ratings.keys())    

        if transfer_n == 0 or transfer_n > len(ordered_image_list):
            transfer_n = len(ordered_image_list)
        ordered_image_list = ordered_image_list[0:transfer_n]

        for filename in ordered_image_list:
            input_file_path = os.path.join(input_folder_path, filename)

            # Choose what to do with dupes, weather replace or skip
            if os.path.exists(os.path.join(destination_folder_path, filename)):
                user_response = messagebox.askquestion("Warning", f"{filename} present in {destination_folder_path}.\
                                                    Do you wish to replace {filename} from the {destination_folder_path}?")
                if user_response == "yes":
                    os.remove(os.path.join(destination_folder_path, filename))
                else:
                    skip_n += 1
                    continue

            shutil.move(input_file_path, destination_folder_path)

        self.entry_input_folder_path.delete(0, tk.END)
        self.entry_destination_folder_path.delete(0, tk.END)
        self.entry_csv_path.delete(0, tk.END)
        messagebox.showinfo("Message", f"transfered {transfer_n - skip_n} out of {transfer_n} images to {destination_folder_path}")
            
    def clear_recyclebin(self):
        recyclebin_path = os.path.join(self.current_dir, "recycle_bin")
        shutil.rmtree(recyclebin_path)
        self.create_recyclebin_folder()

    def back(self):
        self.menu_root.deiconify()
        self.root.destroy()

    def close(self):
        self.menu_root.destroy()

class MainMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MainMenu")
        self.root.focus_set()

        button_width = 15
        button_height = 3
        padding = 10

        # Open ImageCompareApp
        self.button_compare = tk.Button(self.root, text="Compare Images", command=self.open_compare, width=button_width, height=button_height)
        self.button_compare.pack(pady=padding, padx=padding)

        # Open ImageDisplayApp
        self.button_display = tk.Button(self.root, text="Display elo results", command=self.open_display, width=button_width, height=button_height)
        self.button_display.pack(pady=padding, padx=padding)

        # Open ImageTransferApp
        self.button_transfer = tk.Button(self.root, text="Transfer images", command=self.open_transfer, width=button_width, height=button_height)
        self.button_transfer.pack(pady=padding, padx=padding)

    def open_compare(self):
        self.image_compare_app = tk.Toplevel(self.root)
        image_compare_app = ImageCompareApp(self.image_compare_app, self.root)
        self.root.withdraw()

    def open_display(self):
        self.image_display_app = tk.Toplevel(self.root)
        image_display_app = ImageDisplayApp(self.image_display_app, self.root)
        self.root.withdraw()

    def open_transfer(self):
        self.image_transfer_app = tk.Toplevel(self.root)
        image_transfer_app = ImageTransferApp(self.image_transfer_app, self.root)
        self.root.withdraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()