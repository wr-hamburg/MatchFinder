import re

markdown=[]
with open('markdown','r') as file:
    for line in file:
        markdown.append(line)

csv=[]
for line in markdown:
    found=re.findall('(?:\*\s*)(.*?)(?:\(\()(.*)(?:\)\))',line)
    if found:
        topicDateTutor=''
        for x in found[0]:
            topicDateTutor+=x.strip()
            topicDateTutor+=', '
        csv.append(topicDateTutor.strip(', '))

with open('parsedTopics.csv','w') as file:
    for line in csv:
        file.write(line+'\n')