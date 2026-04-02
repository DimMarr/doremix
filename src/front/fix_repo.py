with open("repositories/playlistRepository.ts", "r") as f:
    text = f.read()
# Remove all backticks from the last few lines that got corrupted

lines = text.split("\n")
cleaned = []
for line in lines:
    if line.startswith("`"):
        line = line[1:]
    line = line.replace("\`", "`")
    cleaned.append(line)

with open("repositories/playlistRepository.ts", "w") as f:
    f.write("\n".join(cleaned))
