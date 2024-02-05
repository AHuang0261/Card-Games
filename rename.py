import os, glob

path = R"C:\Users\alexa\Downloads\PNG-cards-1.3\PNG-cards-1.3"
pattern = path + "*.png"
result = glob.glob(pattern)
for file in result:
    print(file)
    parts = file.split('_')
    print(parts[0])
    if parts[0] == "ace":
        new_name = f"14_{parts[1]}_{parts[2]}"
        os.rename(file, new_name)
        print(new_name)

