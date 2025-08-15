import random
import os
from operator import itemgetter
import csv


class RhymeTest:
    """ Base class for conducting rhyme-based tests.

    Attributes:
        wordDict (dict): Contains word lists with a specific key for each word list.
        testIterations (int): Number of iterations in a complete test.
        testItemNumber (int): Number of items in each test.
        numberOfConditions (int): Number of conditions in the test.
        indexPool (dict): Stores test indexes for word and condition assignments, i.e., {test_number: {item_index:[[word_index, condition_index],[],[],...]}}.
                          word_index hints to the correct answer and used to play the sound file, condition_index ranges from 0 to numberOfConditions -1
        itemsToDisplay (list): Stores words arranged according to display rules for each test
        responsesWithAnswers (dict): Stores responses and correct answers per condition, i.e., {test_number:[{}]}
        wordItemIndex (int): Tracks the current word item index.
        currentCycle (int): Tracks the current iteration cycle.
        numOfListWords (int): Number of words in each item of test

    """

    def __init__(self, testIterations, testItemNumber, numberOfConditions, testName,trapConditions):
        self.wordDict = {}
        self.testIterations = testIterations
        self.testItemNumber = testItemNumber
        self.numberOfConditions = numberOfConditions
        self.testName = testName
        self.trapConditions = trapConditions

        self.numOfListWords = None
        self.featureTags = None
        self.indexPool = {}
        self.itemsToDisplay = []
        self.responsesWithAnswers = {}
        self.wordItemIndex = 1
        self.currentCycle = 0

    def loadWordList(self, filename, is_mrt=False):
        """
        Load the word list from the file and associate word pairs with features explicitly,
        including 'Trapconditions' as a valid feature.
        """
        with open(filename, 'r', encoding='utf-8') as wordFile:
            featureTag = {key: [] for key in self.features}  # Initialize feature tags
            current_feature = None  # Track the current feature being processed
            count = 0

            for line in wordFile:
                line = line.strip()

                # Check for feature label (e.g., Voicing, Nasality)
                if line.title() in self.features:
                    current_feature = line.title()  # Update the current feature
                    continue

                # Process word pair lines
                if '-' in line and current_feature:
                    key = int(line.split('.')[0])  # Extract the numeric key
                    data = line.split('.')[1].split('-')  # Extract the word pair
                    data = [word.strip() for word in data]  # Clean the words

                    # Store the word pair in the word dictionary
                    self.wordDict[key] = data

                    # Add the key to the current feature's tag
                    featureTag[current_feature].append(key)
                    count += 1

                # Stop when required number of items is processed
                if count == self.testItemNumber + self.trapConditions:
                    break

        # Update class attributes
        print(f'Word Dictionary: {self.wordDict}')
        self.numOfListWords = len(self.wordDict[list(self.wordDict.keys())[0]])
        self.testItemNumber = len(self.wordDict)
        self.featureTags = featureTag
        print('Feature Tags:', self.featureTags)

    def findFeatureTag(self, index):
        # Find the feature tag associated with a given index
        for key in self.featureTags.keys():
            if index in self.featureTags[key]:
                return key

    def createIndexPool(self):
        """Creates an index pool for the test."""
        # Initialize indexPool with empty lists for each wordDict key
        indexPool = {key: [] for key in self.wordDict.keys()}
        trap_condition_items = self.featureTags.get('Trapconditions', [])
        # Fill indexPool with shuffled indices and assign conditions
        for key in self.wordDict.keys():
            temp_pool = list(range(self.numOfListWords))
            indices = []
            for _ in range(self.testIterations * self.numberOfConditions):
                if not temp_pool:
                    temp_pool = list(range(self.numOfListWords))
                random_index = random.choice(temp_pool)
                temp_pool.remove(random_index)
                indices.append([random_index])
            indices.sort(key=itemgetter(0))  # Sort by index
            conditionCount = 0
            for idx in indices:
                if key in trap_condition_items:
                    idx.append(0)
                else:
                    idx.append(conditionCount)
                    conditionCount = (conditionCount + 1) % self.numberOfConditions
            indexPool[key] = indices

        # Build self.indexPool with randomized selections
        self.indexPool = {test: {key: [] for key in self.wordDict.keys()} for test in
                          range(1, self.numberOfConditions + 1)}
        for test in range(1, self.numberOfConditions + 1):
            for key in self.wordDict.keys():
                for _ in range(self.testIterations):
                    if indexPool[key]:
                        selected_pair = random.choice(indexPool[key])
                        self.indexPool[test][key].append(selected_pair)
                        indexPool[key].remove(selected_pair)

        print(f'Index Pool: {self.indexPool}')

    def getCycleNum(self):
        return self.testIterations

    def getNumOfListWords(self):
        return self.numOfListWords

    def gettestItemNumber(self):
        return self.testItemNumber

    def arrangeWordOrderings(self):
        """Arrange word orderings for each cycle."""
        for _ in range(self.testIterations):
            shuffledKeys = list(self.wordDict.keys())
            random.shuffle(shuffledKeys)

            wordItems = {}

            for key in shuffledKeys:
                wordPairs = self.wordDict[key].copy()
                # Randomly shuffle the word pairs
                random.shuffle(wordPairs)
                wordItems[key] = wordPairs
            self.itemsToDisplay.append(wordItems)

        print(f'Items after reversal: {self.itemsToDisplay}')

    def storeAnswers(self, test_number, condition, item_index, word_index, word):
        """Stores the answers of a subject for a question."""
        if test_number not in self.responsesWithAnswers:
            self.responsesWithAnswers[test_number] = []

        correct_answer = self.wordDict[item_index][word_index]
        self.responsesWithAnswers[test_number].append({"Item Index": item_index,
                                                       "Word Index": word_index,
                                                       "Condition": condition,
                                                       "Answer Pair": [correct_answer, word]})

    def saveTestQuestionsAndAnswers(self, subject_name, user_id, answerDir, is_trial):
        """Saves both test questions and answers in a single file."""
        suffix = "_trial" if is_trial else ""
        filename = os.path.join(answerDir, f"{subject_name}_{user_id}_results{suffix}.txt")

        print("Responses:", self.responsesWithAnswers)
        with open(filename, 'w') as file:
            # Write header
            file.write("Test Number, Trial Number, Item Index, Word Index, Condition, Correct Answer, Answer\n")

            for test_number in self.responsesWithAnswers:
                for trial_num in range(len(self.responsesWithAnswers[test_number])):

                    # Store the question details
                    file.write(f"{test_number}, {trial_num}, {self.responsesWithAnswers[test_number][trial_num]['Item Index']}, {self.responsesWithAnswers[test_number][trial_num]['Word Index']}, {self.responsesWithAnswers[test_number][trial_num]['Condition']}, ")
                    correct_answer, answer = self.responsesWithAnswers[test_number][trial_num]["Answer Pair"]

                    # Write the answer and correct answer to the file
                    file.write(f"{answer}, {correct_answer}\n")

    def getItemToDisplay(self, test_number):

        print("Item to display:", self.itemsToDisplay)

        if self.currentCycle >= self.testIterations:
            return None, None, None, None

        trap_condition_items = self.featureTags.get('Trapconditions', [])
        cycle_items = self.itemsToDisplay.copy()
        if self.trapConditions > 0:
            if self.wordItemIndex > self.testItemNumber-self.trapConditions+1:
                self.wordItemIndex = 1
                self.currentCycle += 1
                if self.currentCycle == self.testIterations:
                    return None, None, None, None
            for cycle_index in range(self.testIterations):
                current_cycle_items = cycle_items[cycle_index]

                for itemIndex in current_cycle_items:
                    if itemIndex in trap_condition_items:
                        assigned_item_index = trap_condition_items[(test_number - 1) % len(trap_condition_items)]
                        cycle_items[cycle_index] = {
                            key: value for key, value in current_cycle_items.items()
                            if key == assigned_item_index or key not in trap_condition_items
                        }

                        # Log for debugging the selected trap condition item
                        print(
                            f"Selected trap condition item for cycle {cycle_index + 1}, test {test_number}: {assigned_item_index}")
                        print('cycle_items',cycle_items)
        else:
            if self.wordItemIndex > self.testItemNumber:
                self.wordItemIndex = 1
                self.currentCycle += 1
                if self.currentCycle == self.testIterations:
                    return None, None, None, None
        itemIndex = list(cycle_items[self.currentCycle].keys())[self.wordItemIndex - 1]
        item = cycle_items[self.currentCycle][itemIndex]

        # Now retrieve the wordIndex and conditionIndex for the current item
        wordIndex, conditionIndex = self.indexPool[test_number][itemIndex][self.currentCycle]

        # Move to the next item
        self.wordItemIndex += 1

        # Print the details of the selected item
        print(
            f'Item {item}, Word Index {wordIndex}, Item Index {itemIndex}, Cycle {self.currentCycle}, Condition {conditionIndex}')

        # Return the necessary details
        return item, wordIndex, itemIndex, conditionIndex

    def calculatePerformance(self, subject_name,code, user_id, gender, age, lang, answerDir, is_trial, durations, num_response_alternatives):
        """Calculate and record the performance of the test."""
        print("Num of Response Alternatives", num_response_alternatives)
        # Initialize correctResponses to track correct and incorrect responses for each condition and feature
        correctResponses = {}

        # Collect all unique conditions and initialize response tracking
        for test_number, responses in self.responsesWithAnswers.items():
            for response in responses:
                condition = response["Condition"]
                if condition not in correctResponses:
                    correctResponses[condition] = {key: {'R': 0, 'W': 0} for key in self.features}
                    correctResponses[condition]['Overall'] = {'R': 0, 'W': 0}  # Initialize 'Overall'

        # Process responses to count correct (R) and incorrect (W)
        for test_number, responses in self.responsesWithAnswers.items():
            for response in responses:
                condition = response["Condition"]
                correct_answer = response["Answer Pair"][0]
                user_answer = response["Answer Pair"][1]
                feature = self.findFeatureTag(response["Item Index"])

                if correct_answer.lower() == user_answer.lower():
                    correctResponses[condition][feature]['R'] += 1
                    if feature != 'Trapconditions':
                        correctResponses[condition]['Overall']['R'] += 1
                else:
                    correctResponses[condition][feature]['W'] += 1
                    if feature != 'Trapconditions':
                        correctResponses[condition]['Overall']['W'] += 1

        print("Correct Responses:", correctResponses)
        # Handle trial mode: return overall performance for the last condition
        if is_trial:
            last_condition = list(correctResponses.keys())[-1]
            R = correctResponses[last_condition]['Overall']['R']
            W = correctResponses[last_condition]['Overall']['W']
            return (R - W / (num_response_alternatives-1)) / (R + W) * 100

        # Handle language format
        lang = lang.split(',')[1] if ',' in lang else lang

        # Prepare results for each condition and write to CSV
        file_path = os.path.join(answerDir, f'{self.testName}_subjectivePerformance.csv')
        file_exists = os.path.exists(file_path)
        header_written = False

        with open(file_path, "a", newline='') as f:
            writer = csv.writer(f)

            for condition in correctResponses.keys():
                # Prepare header and row for this condition
                header = ["Subject Name",'completion_code', 'user_id', 'Gender', 'Age', "Native", "Condition"]
                row = [subject_name,code, user_id, gender, age, lang, condition]

                for feature in correctResponses[condition]:
                    R = correctResponses[condition][feature]['R']
                    W = correctResponses[condition][feature]['W']
                    if R+W == 0:
                        performance_value = 0
                    else:
                        performance_value = (R - W / (num_response_alternatives - 1)) / (R + W) * 100
                    row.append(performance_value)
                    header.append(f"{feature} Performance (%)" if feature != "Overall" else "Overall Performance (%)")

                # Write header only once
                if not header_written:
                    writer.writerow(header)
                    header_written = True

                writer.writerow(row)

        print('Performance recorded')


class MRT(RhymeTest):
    def __init__(self, testIterations, testItemNumber, numberOfConditions, testName,trapConditions):
        super().__init__(testIterations, testItemNumber, numberOfConditions, testName, trapConditions)

        self.features = ["Initial Consonants", "Final Consonants",'Trapconditions']

    def startTest(self, filename):
        self.loadWordList(filename, is_mrt=True)
        self.createIndexPool()
        self.arrangeWordOrderings()

    def reset(self):
        self.wordItemIndex = 1
        self.currentCycle = 0
        self.itemsToDisplay = []
        self.arrangeWordOrderings()


class DRT(RhymeTest):
    def __init__(self, testIterations, testItemNumber, numberOfConditions, testName, trapConditions):
        super().__init__(testIterations, testItemNumber, numberOfConditions, testName, trapConditions)

        self.features = ["Voicing", "Nasality", "Sustension", "Sibilation", "Graveness", "Compactness",'Trapconditions']

    def startTest(self, filename):
        ''' Load word list, create index pool, and arrange word orderings '''
        self.loadWordList(filename, is_mrt=False)
        self.createIndexPool()
        self.arrangeWordOrderings()

    def reset(self):
        self.wordItemIndex = 1
        self.currentCycle = 0
        self.itemsToDisplay = []
        self.arrangeWordOrderings()
