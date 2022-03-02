from random import randrange
from faker import Faker

fake = Faker('de_DE')

def createDummyStineList(amountOfStudents):
    users=[]
    i=1

    for user in range (amountOfStudents):
        id=i
        vorname=fake.first_name()
        nachname=fake.last_name()
        matrikelnummmer=randrange(1111111,9999999)
        i+=1
        line=str(id)+'\t'+str(matrikelnummmer)+'\t'+nachname+'\t'+vorname+'\t'
        users.append(line)

    with open('stineDummyList.txt','w') as file:
        for line in users:
            file.write(line+'\n')


def createDummyTopics(amountOfTopics):
    topics=[]

    for number in range (amountOfTopics):
        topicName=fake.catch_phrase()
        date=fake.future_date()
        name=fake.name()
        line=topicName+','+date.strftime('%d.%m.%Y')+','+name
        topics.append(line)

    with open('dummyTopicsList.csv','w') as file:
        for line in topics:
            file.write(line+'\n')

# createDummyStineList(20)
# createDummyTopics(20)