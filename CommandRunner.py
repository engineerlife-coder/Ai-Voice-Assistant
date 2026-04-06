#pip install pycaw#i dont wanna do stuff like this to this code but its for the ai so it just needs the functionality like that
#windows api thing
#pip install pyautogui
#simulate the key press

import pyautogui

#test dummy cpu

#example code add, 5, 5, set, x, output, get, x, print, output

debug = False

code_words = ["print", "add", "set", "get", "if", "notif", "volume", "exit"]


code_word_argument_count = {#this is good becuase you can easily add more key words to the look up, except no need bc the name dont, its redundant so ima reuse this to tell the arguement numbers so it can check that and not have to run the code
    "print": 1,#its also easily changeable for the look ups, and i was on a crazy brain wave
    "add": 2,#so i dont really know why i did this of all systems of all aproaches
    "set": 2,#ig i was thinking like oh you can call add and it will DIRECT convert it to python
    "get": 1,#and then sub the add to + so its print(5 + 5), instead of print, 5, add, 5 or whatever
    "if": 3,#this checks if something is true and if so it runs code
    "notif": 3,#this checks if something is not true and if so it runs code, ig when i fix it its be if, 5, =, 5
    "volume":1,#this changes the volume by the balue given to it, its an addition for the ai
    "exit":1,#this closes the program and it relys upon local vs non local execution for the navi plug in, but only if the next arguement is true
}

ram = {}

code_error = ""

class CP:
    
    def get_input(input_text):
        global code_words
        x = 0
        hold = ""
        code = []
        arguments = []
        while x < len(input_text):
            if not input_text[x] == ",":
                hold = hold + input_text[x]
            else:
                if hold.lower() in code_words:
                    if debug:
                        print(f"{hold} accepted as a key world")
                    #hold = hold + '*'
                    code.append(hold.lower().strip())
                else:
                    if debug:
                        print(f"{hold} is not a key word, accepting as an argument")
                    arguments.append(hold.lower().strip())
                hold = ""
            x += 1
        if hold.lower() in code_words:
            if debug:
                print(f"{hold} accepted as a key world")
            #hold = hold + '*'
            code.append(hold.lower().strip())
        else:
            if debug:
                print(f"{hold} is not a key word, accepting as an arguemnt")
            arguments.append(hold.lower().strip())
        if debug:
            print(code)
            print(arguments)
        return code, arguments
        
    def run_code(code, arguments):#setting it to false if true not given so it just runs normally unless u tell it ur testing, local testing is to see if ur testing it locally so then it will shut down this or the other thing
        global debug, ram, code_error#both true by defualt bc if ur running it here ur testing thus it shouldnt mess with anything or try to close the navi
        code_error = ""
        x = 0
        x1 = -1
        output = ''
        if debug:
            print(f"Length of code is:{len(code)}, lenght of arguments is:{len(arguments)}")
        while x < len(code):
            try:
                if debug:
                    print(f"Processing {code[x]} to run")
                    
                if code[x] == "print":#there is no way to make it more effecient
                    x1 += 1
                    if arguments[x1] == "output":
                        print(output)
                    else:
                        print(arguments[x1])#because each thing is its own thing it cant really be modular
                    #return code[x], this will end the code, i will make a differnt way for getting data later
                    #and yep i did, i used the code scanner and just added to arguments instead and add a 2nd list

                elif code[x] == "add":
                    x1 += 2
                    total = int(arguments[x1 - 1]) + int(arguments[x1])
                    output = total
                    #will be removed later once i get this working, and it was, no more print ran
                    #return number1 + number2, this will end the code, i will make a differnt way for getting data later

                elif code[x] == "set":#get and set ram, not much yaping needed
                    x += 1
                    if arguments[x1] == "output":
                        ram[arguments[x1]] = output#plus it just makes it look better and cleaner
                    else:
                        x1 += 1
                        ram[arguments[x1 - 1]] = arguments[x1]#plus it just makes it look better and cleaner

                elif code[x] == "get":
                    x1 += 1
                    output = ram[arguments[x1]]

                elif code[x] == "if":
                    x+= 2
                    if not arguments[x1 - 1] == arguments[x1]:
                        x += 1#skip next word after arguments aka next keyword/command

                elif code[x] == "notif":
                    x+= 2
                    if arguments[x1 - 1] == arguments[x1]:
                        x += 1#skip next word after arguments aka next keyword/command

                elif code[x] == "volume":
                    x1 += 1
                    if arguments[x1] == "output":
                        volume = output
                    else:
                        volume = arguments[x1]
                        
                    steps = max(-50, min(50, int(volume)))#ai but good for like range like can only do max +50 or min -50
                    for _ in range(abs(steps)):#ai made it and its super easy to just do it
                        if steps > 0:
                            pyautogui.press("volumeup")#if i knew this i coulda done it but ai did
                        else:
                            pyautogui.press("volumedown")
                        
                    if steps < 0:
                        return f"Turned your volume down by {abs(steps)}."
                    else:
                        return f"Turned your volume up by {abs(steps)}."

                elif code[x] == "exit":#ai based only
                    x1 += 1
                    if arguments[x1].lower() == "true":
                        conformation = str(input("Close program? Y/N:"))
                        if conformation.lower() == "y":
                                quit()#closes the main file too
                        else:
                            return "User premission not granted"
                    else:
                        return("Ai permission not granted")
                else:
                    return("CODE FAILED, ERROR: FUNCTION NOT ADDED")

                x += 1
                if debug:
                    print(f"x is currently:{x}, x1 is currently:{x1}, output is currently:{output}")

            except Exception as e:#added new from ai but it makes sicne and now i know more (KeyError, ValueError, IndexError) old
                error_name = type(e).__name__#more ai but im learning
                code_error = error_name
                if isinstance(e, KeyError):
                    return("Hint:Check that the variable is created before trying to retrive it")
                return(f"There is an error in your code, python gave me this error message so here you go {error_name}, Here is the code, {code}, and the arguments, {arguments}")
    
    def test_code(code, arguments):
        global code_word_argument_count
        ac = 0#argument count to make sure it matches
        for i in code:#for the length of code search up the arguments needed add em up and move on
            ac += code_word_argument_count[i]
        if ac == len(arguments):#same amount of arguements as used, thus the code 100% works no missalignments or extra arguements ect
            return True
        else:
            return False
        
        
    """
    def test_code(code):
        global code_words
        x = 0
        fail = False
        while x < len(code):#dont end keep going so you get all errors
            if not code[x] in code_words:
                fail = True
        if not fail:
            return True
        else:
            return False
        """
    
    """
    def test_code(code, arguments):
        global code_error
        CP.run_code(code, arguments, True)
        if code_error == "":#this is enneficeent but it just checks if the code runs plus its so light nothing bad really happens plus its needed and the only way i can think of and python kinda does the same thing except it just doesnt run the code it just does more advanced checking stuff so that those errors are caught or then again they trigger whilst running whatever
            return True#no error
        else:
            return False
        #old dumb method now ima just ahve it check the code to the arguments
    """

            
if __name__ == "__main__":#wow already there just in case
    try:
        debugging = str(input('Debug mode? Type yes or no:'))
        if debugging.lower() == 'yes':
            debug = True
        elif debugging.lower() == 'no':
            debug = False
        else:
            print('Please only type "Yes" or "No", defualting to no debug mode.')
            debug = False
    except ValueError:
        print('Please only type "True" or "False", defualting to debug mode.')
        debug = False
    while True:
        test = str(input("Test:"))
        code, arguments = CP.get_input(test)
        if CP.test_code(code, arguments):#adding back the test for the ai bc its gonna be like giving commands but only sometimes
            CP.run_code(code, arguments)
        else:
            print("Code failed")
        #CP.run_code(code, arguments)