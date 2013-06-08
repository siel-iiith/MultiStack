def fillDict(j,dictionary):
	if j in dictionary:
		dictionary[j]+=1
	else:
		dictionary[j]=1


def makeDict(individualList):
	dictionary={}
	[  fillDict(j.strip(),dictionary) for i in individualList for j in i[2] ]
	return dictionary
