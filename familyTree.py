"""
Brandon Wong
CPSC 3400
HW 2: Family Trees
4/22/2022
The code that I am submitting is original code and has not been copied
from another source. I have written all the code I am submitting beyond
the starting code from the given descendants.py file.

GEDCOM parser design

Create empty dictionaries of individuals and families
Ask user for a file name and open the gedcom file
Read a line
Skip lines until a FAM or INDI tag is found
    Call functions to process those two types

Processing an Individual
Get pointer string
Make dictionary entry for pointer with ref to Person object
Find name tag and identify parts (surname, given names, suffix)
Find FAMS and FAMC tags; store FAM references for later linkage
Skip other lines

Processing a family
Get pointer string
Make dictionary entry for pointer with ref to Family object
Find HUSB WIFE and CHIL tags
    Add included pointers to Family object
Skip other lines

Testing to show the data structures:
    Print info from the collections of Person and Family objects
    Print descendant chart after all lines are processed

"""

from collections import namedtuple

#-----------------------------------------------------------------------

class Person():
    # Stores info about a single person
    # Created when an Individual (INDI) GEDCOM record is processed.
    #-------------------------------------------------------------------

    def __init__(self,ref):
        # Initializes a new Person object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._asSpouse = []  # use a list to handle multiple families
        self._asChild = None
        self._events = []
                
    def addName(self, names):
        # Extracts name parts from a list of names and stores them
        self._given = names[0]
        self._surname = names[1]
        self._suffix = names[2]

    def addIsSpouse(self, famRef):
        # Adds the string (famRef) indicating family in which this person
        # is a spouse, to list of any other such families
        self._asSpouse.append(famRef)
        
    def addIsChild(self, famRef):
        # Stores the string (famRef) indicating family in which this person
        # is a child
        self._asChild = famRef

    def printDescendants(self, prefix=''):
        # print info for this person and then call method in Family
        print(prefix + self.name() + " " + self.getEvents())
        # recursion stops when self is not a spouse
        for fam in self._asSpouse:
            families[fam].printFamily(self._id,prefix)

    def name (self):
        # returns a simple name string 
        return self._given + ' ' + self._surname.upper()\
               + ' ' + self._suffix
    
    def treeInfo (self):
        # returns a string representing the structure references included in self
        if self._asChild: # make sure value is not None
            childString = ' | asChild: ' + self._asChild
        else: childString = ''
        if self._asSpouse != []: # make sure _asSpouse list is not empty
            # Use join() to put commas between identifiers for multiple families
            # No comma appears if there is only one family on the list
            spouseString = ' | asSpouse: ' + ','.join(self._asSpouse)
        else: spouseString = ''
        return childString + spouseString
    
    def eventInfo(self):
        ## add code here to show information from events once they are recognized
        return self.getEvents()

    def __str__(self):
        # Returns a string representing all info in a Person instance
        # When treeInfo is no longer needed for debugging it can 
        return self.name() \
                + self.eventInfo()  \
                + self.treeInfo()  ## Comment out when not needed for debugging

    def isDescendant(self, personID):
        # Base case: returns True if personID is themselves
        if self._id == personID:
            return True
        # For every person in the family, recursively check if they are a descendant
        for fam in self._asSpouse:
            if families[fam].isDescendantHelper(personID):
                return True
        return False

    def printAncestors(self, prefix='', level=0):
        # Find the family in which this person is the child, then recursively call onto their parents
        if self._asChild is not None:
            families[self._asChild].printAncestorsSpouse1(prefix, level)
        print(prefix + str(level) + " " + self.name() + ' ' + self._id+ ' ' + self.getEvents())
        if self._asChild is not None:
            families[self._asChild].printAncestorsSpouse2(prefix, level)

    # Adds an event to the person's event list
    def addEvent(self, event):
        self._events.append(event)

    # Returns a string with all the event information
    def getEvents(self):
        ret = ''
        for e in self._events:
            ret += e.getInfo() + ' '
        return ret

    # Returns the family (or families) in which the person is a spouse
    def getAsSpouse(self):
        return self._asSpouse

    # Returns the family (or families) in which the person is a child
    def getAsChild(self):
        return self._asChild

    # Implementation for printing first cousins
    def printCousins(self, n=1):
        print("First cousins for ", self.name())
        cousins = list()
        grandparent_family = set()
        parents = set()
        # Find family in which person is the child
        if self._asChild is not None:
            for p in families[self._asChild].getParents():
                if p is not None:
                    # Add their parents to a set
                    parents.add(p)
            # Get the families for the person's grandparents
            for p in families[self._asChild].getParentsAsChild():
                if p is not None:
                    grandparent_family.add(p)
            for fam in grandparent_family:
                # For each child in the grandparent family that is not the original
                # parents, get their children and add to the list of cousins
                for parent in getFamily(fam).getChildren():
                    if parent not in parents:
                        for family in getPerson(parent).getAsSpouse():
                            for child in getFamily(family).getChildren():
                                if child not in cousins:
                                    cousins.append(child)
        if cousins:
            for c in cousins:
                print("   " + getPerson(c).name() + getPerson(c).getEvents())
        else:
            print("   No cousins")



# end of class Person
 
#-----------------------------------------------------------------------

# Declare a named tuple type used by Family to create a list of spouses
Spouse = namedtuple('Spouse',['personRef','tag'])

class Family():
    # Stores info about a family
    # An instance is created when an Family (FAM) GEDCOM record is processed.
    #-------------------------------------------------------------------


    def __init__(self, ref):
        # Initializes a new Family object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._spouse1 = None
        self._spouse2 = None
        self._children = []
        self._events = []

    def addSpouse(self, personRef, tag):
        # Stores the string (personRef) indicating a spouse in this family
        newSpouse = Spouse(personRef, tag)
        if self._spouse1 == None:
            self._spouse1 = newSpouse
        else: self._spouse2 = newSpouse

    def addChild(self, personRef):
        # Adds the string (personRef) indicating a new child to the list
        self._children.append(personRef)
        
    def printFamily(self, firstSpouse, prefix):
        # Used by printDecendants in Person to print other spouse
        # and recursively invoke printDescendants on children

        # Manipulate prefix to prepare for adding a spouse and children
        if prefix != '': prefix = prefix[:-2]+'  '
        
        # Print out a '+' and the name of the second spouse, if present
        if self._spouse2:  # check for the presence of a second spouse
            # If a second spouse is included, figure out which is the
            # "other" spouse relative to the descendant firstSpouse
            if self._spouse1.personRef == firstSpouse:
                secondSpouse = self._spouse2.personRef
            else: secondSpouse = self._spouse1.personRef
            print(prefix+ '+' + persons[secondSpouse].name())

        # Make a recursive call for each child in this family
        for child in self._children:
             persons[child].printDescendants(prefix+'|--')
        
    def __str__(self):
        ## Constructs a single string including all info about this Family instance
        spousePart = ''
        for spouse in (self._spouse1, self._spouse2):  # spouse will be a Spouse namedtuple (spouseRef,tag)
            if spouse:  # check that spouse is not None
                if spouse.tag == 'HUSB':
                    spousePart += ' Husband: ' + spouse.personRef
                else: spousePart += ' Wife: ' + spouse.personRef
        childrenPart = '' if self._children == [] \
            else' Children: ' + ','.join(self._children)
        return spousePart + childrenPart

    # Helper function for isDescendant which checks every member of the family if they are a descendant of personID
    def isDescendantHelper(self, personID):
        for child in self._children:
            if persons[child].isDescendant(personID):
                return True

    # Helper function for printAncestors that prints Spouse1's side of the parent's family
    def printAncestorsSpouse1(self, prefix, level: int):
        if self._spouse1 is not None:
            persons[self._spouse1.personRef].printAncestors(prefix+'   ', level+1)

    # Helper function for printAncestors that prints Spouse2's side of the parent's family
    def printAncestorsSpouse2(self, prefix, level: int):
        if self._spouse2 is not None:
            persons[self._spouse2.personRef].printAncestors(prefix+'   ', level+1)

    # Function to add a marriage event to the family, and to each of the parents in that family
    def addEvent(self, event):
        self._events.append(event)
        if event.getType() == 'MARR':
            if self._spouse1 is not None:
                persons[self._spouse1.personRef].addEvent(event)
            if self._spouse2 is not None:
                persons[self._spouse2.personRef].addEvent(event)

    # Function that returns a string of the family events
    def getEvents(self):
        ret = ''
        for e in self._events:
            ret += e.getInfo() + ' '
        return ret

    # Function that returns a list of the parents in the family
    def getParents(self):
        res = []
        if self._spouse1 is not None:
            res.append(self._spouse1.personRef)
        if self._spouse2 is not None:
            res.append(self._spouse2.personRef)
        return res

    # Function that returns a list of families in which the parent is a child
    def getParentsAsChild(self):
        res = []
        if self._spouse1 is not None:
            res.append(getPerson(self._spouse1.personRef).getAsChild())
        if self._spouse2 is not None:
            res.append(getPerson(self._spouse2.personRef).getAsChild())
        return res

    # Function that returns list of children
    def getChildren(self):
        if self._children is not None:
            return self._children

# end of class Family

# -----------------------------------------------------------------------

class Event():
    def __init__(self, tag, date=None, place=None):
        # Initializes a new Event object
        self._type = tag
        self._date = date
        self._place = place

    # Return the type of event
    def getType(self):
        return self._type

    # Function that sets event info
    def setInfo(self, desc, info):
        if desc == 'DATE' and self._date is None:
            self._date = info
        elif desc == 'PLAC' and self._place is None:
            self._place = info

    # Function that returns event info as a string
    def getInfo(self):
        ret = ''
        if self._date is not None or self._place is not None:
            if self._type == 'BIRT':
                ret += 'n: '
            elif self._type == 'DEAT':
                ret += 'd: '
            elif self._type == 'MARR':
                ret += 'm: '
            if self._date is not None:
                ret += self._date + ' '
            if self._place is not None:
                ret += self._place + ' '
        return ret

# end of class Event

#-----------------------------------------------------------------------
# Global dictionaries used by Person and Family to map INDI and FAM identifier
# strings to corresponding object instances

persons = dict()  # saves references to all of the Person objects
families = dict() # saves references to all of the Family objects

## Access functions to map identifier strings to Person and Family objects
## Meant to be used in a module that tests this one

def getPerson (personID):
    return persons[personID]

def getFamily (familyID):
    return families[familyID]

## Print functions that print the info in all Person and Family objects 
## Meant to be used in a module that tests this one
def printAllPersonInfo():
    # Print out all information stored about individuals
    for ref in sorted(persons.keys()):
        print(ref + ':' + str(persons[ref]))
    print()

def printAllFamilyInfo():
    # Print out all information stored about families
    for ref in sorted(families.keys()):
        print(ref + ':' + str(families[ref]))
    print()

#-----------------------------------------------------------------------
 
def processGEDCOM(file):

    def getPointer(line):
        # A helper function used in multiple places in the next two functions
        # Depends on the syntax of pointers in certain GEDCOM elements
        # Returns the string of the pointer without surrounding '@'s or trailing
        return line[8:].split('@')[0]
            
    def processPerson(newPerson):
        nonlocal line
        line = f.readline()
        while line[0] != '0': # process all lines until next 0-level
            tag = line[2:6]  # substring where tags are found in 0-level elements
            if tag == 'NAME':
                names = line[6:].split('/')  #surname is surrounded by slashes
                names[0] = names[0].strip()
                names[2] = names[2].strip()
                newPerson.addName(names)
            elif tag == 'FAMS':
                newPerson.addIsSpouse(getPointer(line))
            elif tag == 'FAMC':
                newPerson.addIsChild(getPointer(line))
            ## add code here to look for other fields
            elif tag == 'BIRT' or tag == 'DEAT':
                line = f.readline()
                newEvent = Event(tag)
                while line[0] == '2':
                    desc = line[2:6].strip()
                    info = line[7:].strip()
                    newEvent.setInfo(desc, info)
                    line = f.readline()
                newPerson.addEvent(newEvent)
                continue

            # read to go to next line
            line = f.readline()

    def processFamily(newFamily):
        nonlocal line
        line = f.readline()
        while line[0] != '0':  # process all lines until next 0-level
            tag = line[2:6]
            if tag == 'HUSB':
                newFamily.addSpouse(getPointer(line),'HUSB')
            elif tag == 'WIFE':
                newFamily.addSpouse(getPointer(line),'WIFE')
            elif tag == 'CHIL':
                newFamily.addChild(getPointer(line))
            ## add code here to look for other fields
            elif tag == 'MARR':
                line = f.readline()
                newEvent = Event(tag)
                while line[0] == '2':
                    desc = line[2:6].strip()
                    info = line[7:].strip()
                    newEvent.setInfo(desc, info)
                    line = f.readline()
                newFamily.addEvent(newEvent)
                continue
            # read to go to next line
            line = f.readline()


    ## f is the file handle for the GEDCOM file, visible to helper functions
    ## line is the "current line" which may be changed by helper functions

    f = open (file)
    line = f.readline()
    while line != '':  # end loop when file is empty
        fields = line.strip().split(' ')
        # print(fields)
        if line[0] == '0' and len(fields) > 2:
            # print(fields)
            if (fields[2] == "INDI"): 
                ref = fields[1].strip('@')
                ## create a new Person and save it in mapping dictionary
                persons[ref] = Person(ref)
                ## process remainder of the INDI record
                processPerson(persons[ref])
                
            elif (fields[2] == "FAM"):
                ref = fields[1].strip('@')
                ## create a new Family and save it in mapping dictionary
                families[ref] = Family(ref) 
                ## process remainder of the FAM record
                processFamily(families[ref])
                
            else:    # 0-level line, but not of interest -- skip it
                line = f.readline()
        else:    # skip lines until next candidate 0-level line
            line = f.readline()

    ## End of ProcessGEDCOM

#-----------------------------------------------------------------------    
## Test code starts here
            
def _main():
    filename = "Kennedy.ged"  # Set a default name for the file to be processed
##    Uncomment the next line to make the program interactive
##    filename = input("Type the name of the GEDCOM file:")

    processGEDCOM(filename)

    printAllPersonInfo()

    printAllFamilyInfo()
    
    person = "I46"  # Default selection to work with Kennedy.ged file
##    Uncomment the next line to make the program interactive
##    person = input("Enter person ID for descendants chart:")

    getPerson(person).printDescendants()

    
if __name__ == '__familyTree__':
    _main()

