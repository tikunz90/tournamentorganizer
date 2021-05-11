import csv
from random import randint

first_names = ['Peeter', 'Thomas', 'Thorsten', 'Sebastian', 'Fritz', 'Lukas', 'Friedrich', 'Max', 'Chris', 'Mario', 'Jens', 'Jonas', 'Julian']
names = ['Schmidt', 'Henkel', 'Mustermann', 'Scheerer', 'Kunz', 'Schreiber', 'Miller', 'Verheul', 'Mun', 'Vorndran', 'Schütz', 'Straßmann', 'Köhler']

n_player = 10
num_start = 1
num = num_start
day = 1
month = 7
year = 1980

data = {}


with open('media/team_new7.csv', 'w+', newline='') as csv_file:
    fieldnames = ['name', 'first_name', 'number', 'birthday']
    writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=fieldnames)
    writer.writeheader()
    for i in range(0, n_player):
        i_first_name = randint(0, len(first_names)-1)
        i_name = randint(0, len(names) - 1)
        num = num + 1
        writer.writerow({'name': names[i_name], 'first_name': first_names[i_first_name], 'number': f'{num}', 'birthday':f'{day:02d}.{month:02d}.{year:04d}'})