import os
import csv
import glob

def load_elo_ratings(folder_path, elo_ratings_csv, new_csv=False):
    """
    Loads a dictionary of images and their respective elos from a folder, and updates/creates the csv from the csv path
    If new_csv is True, the elo ratings of images in the dictonary and the csv file will be set to 1000. 
    This will also be the case if the csv does not exist

    Else, if csv is present in the folder, image paths present in both the csv and the folder will be loaded with their past elo.
    Missing images will be removed from the csv, new images will be added to the csv with a score of 1000.
    """
    elo_ratings = {}

    # Lists all image files in the folder
    image_filenames = images_in_folder(folder_path)

    # Creates a new csv file with all elo initialized to 1000.0
    if os.path.isfile(elo_ratings_csv) == False or new_csv == True:
        with open(elo_ratings_csv, mode="w", newline="") as csvfile:
            fieldnames = ["image_name", "elo"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for image_name in image_filenames:
                writer.writerow({"image_name": image_name, "elo": 1000.0})
    
    # Initialize elo_ratings with initial elo ratings of 1000
    for image_name in image_filenames:
        elo_ratings[image_name] = 1000.0

    # Update elo_ratings with past elo infomation
    with open(elo_ratings_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["image_name"] in image_filenames:
                elo_ratings[row["image_name"]] = float(row['elo'])

    # Sort elo_ratings from highest to lowest
    elo_ratings = sort_dict_by_scores(elo_ratings)
    
    # Create new csv using current elo_ratings
    with open(elo_ratings_csv, mode='w', newline='') as csvfile:
        fieldnames = ["image_name", "elo"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for image_name, elo_score in elo_ratings.items():
            writer.writerow({"image_name": image_name, "elo": elo_score})
            
    return elo_ratings

def sort_dict_by_scores(input_dict, reverse=True):
    """
    Sorts a dictionary by the values in descending order
    """
    sorted_dict = dict(sorted(input_dict.items(), key=lambda item: item[1], reverse=reverse))
    return sorted_dict

def save_elo_ratings(elo_ratings_csv, elo_ratings):
    # Create new csv using current elo_ratings
    with open(elo_ratings_csv, mode='w', newline='') as csvfile:
        fieldnames = ["image_name", "elo"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for image_name, elo_score in elo_ratings.items():
            writer.writerow({"image_name": image_name, "elo": elo_score})

def calculate_expected_score(player_rating, opponent_rating):
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

def caculate_rating(player_rating, opponent_rating, result, k_factor=32):
    expected_score = calculate_expected_score(player_rating, opponent_rating)
    new_rating = round(player_rating + k_factor * (result - expected_score), 2)
    return new_rating

def loading_conflict(folder_path, elo_ratings_csv, in_csv=True):
    """
    Return number of filenames present in csv but not present in folder path or vice versa
    """
    image_filenames = images_in_folder(folder_path)
    csv_filenames = images_in_csv(elo_ratings_csv)

    image_filenames = set(image_filenames)
    csv_filenames = set(csv_filenames)
    
    if in_csv:
        missing_filenames = list(csv_filenames - image_filenames)
    else:
        missing_filenames = list(image_filenames - csv_filenames)
    return len(missing_filenames)

def images_in_folder(folder_path):
    image_paths = []
    image_extensions = ["jpg", "jpeg", "png"]
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, f'*.{ext}')))
    image_filenames = [os.path.basename(image_file) for image_file in image_paths]
    return image_filenames

def images_in_csv(elo_ratings_csv):
    csv_filenames = []
    with open(elo_ratings_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_filenames.append(row["image_name"])
    return csv_filenames

#load_elo_ratings(r"C:\Users\luorr\code\image_rank\images1", new_csv=False)