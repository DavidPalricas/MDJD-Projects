# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import csv
import ast

class ActionCourseInfo(Action):
    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the most recent user message
        latest_message = tracker.latest_message
        
        # Extract entities from the latest message
        entities = latest_message.get('entities', [])
        
        # Look for course-related entities in the current message
        course_info = None
        entity_type = None
        
        for entity in entities:
            if entity['entity'] in ['curso', 'codigo', 'sigla_curso']:
                course_info = entity['value']
                entity_type = entity['entity']
                break
        
        # If no entity in current message, check if we have any in slots
        if not course_info:
            # Check slots in order of preference
            if tracker.get_slot("curso"):
                course_info = tracker.get_slot("curso")
                entity_type = "curso"
            elif tracker.get_slot("sigla_curso"):
                course_info = tracker.get_slot("sigla_curso")
                entity_type = "sigla_curso"
            elif tracker.get_slot("codigo"):
                course_info = tracker.get_slot("codigo")
                entity_type = "codigo"
        
        if course_info:
            # entity_type_display = entity_type.replace("course_", "") if entity_type else "information"
            dispatcher.utter_message(text=f"I see you're interested in the {course_info} course.")
            with open("deti_resourses/curso.csv", 'r', encoding='utf-8') as file:
                # skip the first line (header)
                next(file)
                csv_reader = csv.reader(file)
                
                # Find the course in the CSV file based on the entity type
                for row in csv_reader:
                    match = False
                    
                    if entity_type == "codigo" and course_info.lower() == row[0].lower():
                        match = True
                    elif entity_type == "curso" and course_info.lower() in row[1].lower():
                        match = True
                    elif entity_type == "sigla_curso" and course_info.lower() == row[2].lower():
                        match = True
                    
                    if match:
                        found = True
                        dispatcher.utter_message(text="Here are some details about it:")
                        dispatcher.utter_message(text=f"Course name: {row[1]}")
                        dispatcher.utter_message(text=f"Course code: {row[0]}")
                        dispatcher.utter_message(text=f"Course acronym: {row[2]}")
                        dispatcher.utter_message(text=f"Course's degree: {row[3]}")
                        return []
                
                dispatcher.utter_message(text="Unfortunately I do not have any information about that course.")
                return []
        
        dispatcher.utter_message(text="I understand you're asking about a course, but I couldn't identify which one.")
        dispatcher.utter_message(text="Try specifying the course by its name, code, or acronym.")
        return []

class ActionDisciplinaInfo(Action):
    def name(self) -> Text:
        return "action_disciplina_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the most recent user message
        latest_message = tracker.latest_message
        
        # Extract entities from the latest message
        entities = latest_message.get('entities', [])
        
        # Look for course-related entities in the current message
        disciplina_info = None
        entity_type = None
        
        for entity in entities:
            if entity['entity'] in ['disciplina', 'codigo', 'sigla_disciplina']:
                disciplina_info = entity['value']
                entity_type = entity['entity']
                break
        
        # If no entity in current message, check if we have any in slots
        if not disciplina_info:
            # Check slots in order of preference
            if tracker.get_slot("sigla_disciplina"):
                disciplina_info = tracker.get_slot("sigla_disciplina")
                entity_type = "sigla_disciplina"
            elif tracker.get_slot("disciplina"):
                disciplina_info = tracker.get_slot("disciplina")
                entity_type = "disciplina"
            elif tracker.get_slot("codigo"):
                disciplina_info = tracker.get_slot("codigo")
                entity_type = "codigo"
        
        if disciplina_info:
            # entity_type_display = entity_type.replace("course_", "") if entity_type else "information"
            dispatcher.utter_message(text=f"I see you're interested in the {disciplina_info} subject.")
            
            with open("deti_resourses/disciplinas.csv", 'r', encoding='utf-8') as file:
                # skip the first line (header)
                next(file)
                csv_reader = csv.reader(file)
                found = False
                save_row = None
                
                # Find the disciplina in the CSV file based on the entity type
                for row in csv_reader:
                    match = False
                    if entity_type == "codigo" and disciplina_info.lower() == row[0].lower():
                        match = True
                    elif entity_type == "disciplina" and disciplina_info.lower() in row[2].lower():
                        match = True
                    elif entity_type == "sigla_disciplina" and disciplina_info.lower() == row[1].lower():
                        match = True
                    
                    if match:
                        save_row = row.copy()
                        break

            if save_row:
                dispatcher.utter_message(text="Here are some details about it:")
                dispatcher.utter_message(text=f"Subject name: {save_row[2]}")
                dispatcher.utter_message(text=f"Subject code: {save_row[0]}")
                dispatcher.utter_message(text=f"Subject acronym: {save_row[1]}")
                if(save_row[3] == ""):
                    dispatcher.utter_message(text=f"No information about head teacher.")
                else:
                    dispatcher.utter_message(text=f"Subject's head teacher: {save_row[3]}")

                if(save_row[4] == "MI" or save_row[4] == "M2"):
                    dispatcher.utter_message(text=f"This is a master's class.")
                elif(save_row[4] == "L1"):
                    dispatcher.utter_message(text=f"This is a bachelor's class.")

                # In your action code:
                course_names = get_course_names(save_row[5])  # icursocod is in column 6
                if course_names:
                    dispatcher.utter_message(text="This subject is part of the following courses:")
                    for name in course_names:
                        dispatcher.utter_message(text=f"- {name}")
                else:
                    dispatcher.utter_message(text="Could not find any course information for this subject.")

                if(save_row[6] == "1º SEMESTRE"):
                    dispatcher.utter_message(text=f"First semester")
                else:
                    dispatcher.utter_message(text=f"Second semester")

                return []
            
            else:
                dispatcher.utter_message(text="Unfortunately I do not have any information about that subject.")
                return []
        else:
            dispatcher.utter_message(text="I understand you're asking about a subject, but I couldn't identify which one.")
            dispatcher.utter_message(text="Try specifying the subject by its name, code, or acronym.")

        return []
    
class ActionProfessorInfo(Action):
    def name(self) -> Text:
        return "action_professor_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                
        professor = tracker.get_slot("professor")

        name = tracker.get_slot("user_name")

        if professor:  
            with open("deti_resourses/docentes.csv", 'r', encoding='utf-8') as file:
                next(file)
                csv_reader = csv.reader(file)
                
                for row in csv_reader:
                    match = False

                    professor_name = self.get_professor_name(row[0])
                    
                    if professor.lower() == professor_name.lower():
                        match = True
                    
                    if match:
                        information_message = f"Here, {name}, are some details about Professor {professor}:" if name else f"Here are some details about Professor {professor}:"
                        dispatcher.utter_message(text=information_message)
                        dispatcher.utter_message(text=f"👨‍🏫 Professor's name: {row[0]}")
                        dispatcher.utter_message(text=f"📧 Professor's email: {row[1]}")
                        dispatcher.utter_message(text=f"🏢 Professor's office: {row[2]}")
                        return []
                    
                dispatcher.utter_message(text=f"Unfortunately I do not have any information about professor {professor}.")

                return []
            
        dispatcher.utter_message(text="I didn't catch the name of the professor you're asking about, please ask again.")

        return []
    
    
    def get_professor_name(self, professor_full_name):
        
            profesor_names = professor_full_name.split()

            if len(profesor_names) == 0:
                return ""
            
            if len(profesor_names) == 1:
                return profesor_names[0]
        
            return f"{profesor_names[0]} {profesor_names[-1]}"
    
class ActionEmailInfo(Action):
    def name(self) -> Text:
        return "action_email_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email = tracker.get_slot("email")

        if email:      
            with open("deti_resourses/docentes.csv", 'r', encoding='utf-8') as file:
                next(file)
                csv_reader = csv.reader(file)

                user_name = tracker.get_slot("user_name")
                
                for row in csv_reader:
                    match = False

                    if email.lower() == row[1].lower():
                        match = True
                    

                    if match:

                        information_message = f"{user_name}, the  mail belongs to Professor {row[0]}." if user_name else f"The mail belongs to Professor {self.get_professor_name(row[0])}."

                        dispatcher.utter_message(text=information_message)
                        dispatcher.utter_message(text=f"Is office is in locted in: {row[2]}, if you need to visit him.")
                        return []
                    
                dispatcher.utter_message(text=f"Unfortunately I do not have any information about the email {email}.")

                return []
            
        dispatcher.utter_message(text="I didn't catch the email you're asking about, please ask again.")

        return []
    
class ActionCourseListDegree(Action):
    def name(self) -> Text:
        return "action_course_list_degree"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the most recent user message
        latest_message = tracker.latest_message
        
        # Extract entities from the latest message
        entities = latest_message.get('entities', [])
        
        # Look for course-related entities in the current message
        degree_info = None
        
        for entity in entities:
            if entity['entity'] == 'grau':
                degree_info = entity['value']
                break
        
        if degree_info:
            # dispatcher.utter_message(text=f"Here you go, all {degree_info} courses DETI as to offer:")
            normalized_search = normalize_degree(degree_info)
            dispatcher.utter_message(text=f"I will search for all {degree_info} courses in currently DETI.")
            
            with open("deti_resourses/curso.csv", 'r', encoding='utf-8') as file:
                # Skip header
                next(file)
                csv_reader = csv.reader(file)
                found = False
            
                for row in csv_reader:
                    # Check if the degree matches (case-insensitive)
                    if normalize_degree(row[3]) == normalized_search:
                        found = True
                        dispatcher.utter_message(text=f"- {row[1]} ({row[2]})")
                
                if not found:
                    dispatcher.utter_message(text=f"Unfortunately Deti as no {degree_info} courses.")
        
        else:
            dispatcher.utter_message(text=f"Here you have all courses DETI currently as to offer:")
            # If no degree specified, list all courses
            with open("deti_resourses/curso.csv", 'r', encoding='utf-8') as file:
                next(file)
                csv_reader = csv.reader(file)
                
                current_degree = None
                for row in csv_reader:
                    # Group courses by degree
                    if current_degree != row[3]:
                        current_degree = row[3]
                        dispatcher.utter_message(text=f"\n{current_degree}:")
                    dispatcher.utter_message(text=f"- {row[1]} ({row[2]})")
        
        return []

class ActionDisciplinaListCourse(Action):
    def name(self) -> Text:
        return "action_disciplina_list_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
          # Get the most recent user message
        latest_message = tracker.latest_message
        
        # Extract entities from the latest message
        entities = latest_message.get('entities', [])
        
        # Look for course-related entities in the current message
        course_info = None
        semester_info = None
        
        for entity in entities:
            if entity['entity'] in ['curso', 'codigo', 'sigla_curso']:
                course_info = entity['value']
            elif entity['entity'] == 'semestre':
                semester_info = entity['value']
        
        if course_info:
            dispatcher.utter_message(text=f"I'll look for the subjects in {course_info}")
        
            # First, get the course code
            course_code = None
            with open("deti_resourses/curso.csv", 'r', encoding='utf-8') as file:
                next(file)
                csv_reader = csv.reader(file)
                
                for row in csv_reader:
                    if (course_info.lower() == row[0].lower() or  # code
                        course_info.lower() in row[1].lower() or  # name
                        course_info.lower() == row[2].lower()):   # acronym
                        course_code = row[0]
                        course_name = row[1]
                        break
            
            if course_code:
                # Now search for disciplines
                with open("deti_resourses/disciplinas.csv", 'r', encoding='utf-8') as file:
                    next(file)
                    csv_reader = csv.reader(file)
                    found = False
                    
                    for row in csv_reader:
                        icursocod = row[5]
                        if icursocod.startswith('['):
                            course_codes = ast.literal_eval(icursocod)
                        else:
                            course_codes = [icursocod]
                        
                        # Check if this discipline belongs to the course
                        if str(course_code) in map(str, course_codes):
                            # Check semester if specified
                            if semester_info:
                                normalized_semester = normalize_semester(semester_info)
                                if normalized_semester.lower() not in row[6].lower():
                                    continue
                            
                            if not found:
                                found = True
                                if semester_info:
                                    dispatcher.utter_message(text=f"Here are the {semester_info} subjects for {course_name}:")
                                else:
                                    dispatcher.utter_message(text=f"Here are all subjects for {course_name}:")
                            
                            dispatcher.utter_message(text=f"- {row[2]} ({row[1]})")
                    
                    if not found:
                        if semester_info:
                            dispatcher.utter_message(text=f"I couldn't find any subjects for {course_info} in the {semester_info}.")
                        else:
                            dispatcher.utter_message(text=f"I couldn't find any subjects for {course_info}.")
            else:
                dispatcher.utter_message(text=f"I couldn't find a course matching '{course_info}'.")
        
        else:
            dispatcher.utter_message(text="I understand you're asking about a course, but I couldn't identify which one.")
            dispatcher.utter_message(text="Try specifying the course by its name, code, or acronym.")
            return []
        
        return []

def get_course_names(icursocod_list):
    course_names = []
    with open('deti_resourses/curso.csv', 'r', encoding='utf-8') as curso_file:
        curso_reader = csv.reader(curso_file)
        next(curso_reader)  # Skip header
        
        # Convert string representation of list to actual list if needed
        if isinstance(icursocod_list, str):
            if icursocod_list.startswith('['):
                icursocod_list = ast.literal_eval(icursocod_list)
            else:
                icursocod_list = [icursocod_list]
                
        # Create dictionary of course codes to names
        courses = {}
        for row in curso_reader:
            courses[row[0]] = row[1]
            
        # Get names for each course code
        for code in icursocod_list:
            if str(code) in courses:
                course_names.append(courses[str(code)])    
    return course_names

def normalize_degree(degree):
    # Remove 's and convert to lowercase
    return degree.lower().replace("'s", "")

def normalize_semester(semester_text):
    """Convert various semester formats to a standard format"""
    semester_text = semester_text.lower()
    if "first" in semester_text or "1st" in semester_text or "1" in semester_text:
        return "1º semestre"
    elif "second" in semester_text or "2nd" in semester_text or "2" in semester_text:
        return "2º semestre"
    return semester_text
