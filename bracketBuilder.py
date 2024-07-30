# Description:  
# modules ----------------------------------------------------------------------------------------------------------------------------------
import os, json, csv, re, sys, typing, pdb, stat
# txt --------------------------------------------------------------------------------------------------------------------------------------
def usage_txt() -> None:
    prompt = f'#--------------------------------------------------------#\nbracketBuilder Usage: bracketBuilder.py [arg1] [arg2(optional)]\nNo Valid Arguments Provided\n\n--> arg1:\n        -h or help: Display text about how to generate brackets.\n        -a or about: Display text about the bracketBuilder program.\n        -cb or createBracket: Will prompt user for a path if not provided by arg2.\n        "path/to/.csv": attempt to generate a bracket from the specified file.\n--> arg2:\n        "path/to/.csv": when arg1 is cb and arg2 is provided, attempt to generate a bracket from the specified file.\n--> Note: if you provided a path as the only argument and this txt prompted, the path you provided is invalid.\n#--------------------------------------------------------#'
    print(prompt)
def help_txt() -> None:
    prompt = f'#--------------------------------------------------------#\nbracketBuilder Help:\n\n--> Provide a valid path to a .csv:\n        If the .csv cannot be found the program will return invalid path and reprompt.\n--> Provide a validly formatted .csv:\n        If the .csv is not validly formated the program will return invalid .csv format and reprompt.\n--> .CSV file format breakdown:\n        bracket type*, bracket number**, team/athlete name, seed***\n--> Column Info:\n        *Bracket type - specifies the type this bracket is: "se" for single elimination, "de" for double elimination, "rr" for round robin.\n        **Bracket number - specifies which bracket to add this team/athlete to. All entries with the same bracket number and type will enter the same bracket.\n        ***Seed- specifies the athletes seed. If no seeds are provided for any entry in a bracket then athletes will be unseeded. Round robin bracket types do not have seeds.\n#--------------------------------------------------------#'
    print(prompt)
def about_txt() -> None:
    prompt = f'#--------------------------------------------------------#\nbracketBuilder About:\n\n--> This program is a project for CS 361 at Oregon State University by Keegan Forsythe.\n--> The purpose of the program is to read a .CSV file, generate a bracket(s) from its contents, and store the one or more bracket(s) in a .json file.\n#--------------------------------------------------------#'
    print(prompt)
# path, validation, data --------------------------------------------------------------------------------------------------------------------------
def get_valid_path(path:str) -> str:
    """
    Takes a path as argument. validates and reprompts if necessary. returns a valid path.
    """
    prompt = 'Enter Path to .CSV or 1 to exit: ' 
    valid_path = False
    valid_format = False
    while not valid_path or not valid_format:
        valid_path = is_valid_path_to_csv(path)
        if not valid_path:
            if path != 'h':
                path = input(f'Invalid Path: {path} does not lead to .csv.\nSee -help for .csv help\n'+prompt)
            else:
                path = input(prompt)
            if path == '1':
                exit()
            if re.match(r'^(h|-h|--h|help|-help|--help)$', path):
                help_txt()
                continue
            valid_path = is_valid_path_to_csv(path)
        if valid_path:
            valid_format = is_valid_csv_format(path)
        if not valid_format:
            path = input(f'Invalid .csv: {path} is not formatted correctly.\nSee -help for .csv format help\n'+prompt)
            if path == '1':
                exit()
            elif re.match(r'^(h|-h|--h|help|-help|--help)$', path):
                help_txt() 
    return path
def is_valid_path_to_csv(path:str) -> bool:
    """
    True if the path leads to a .csv file.
    param: path is expected to be a lowercase string
    """
    if not path.lower().endswith('.csv'):                    # is the specified file a .csv
        return False
    elif not os.path.isfile(path):                              # does the path lead to the specified .csv file
        return False
    else:
        return True
def is_valid_csv_format(csv_path: str) -> bool:
    """
    Takes a path to a .csv file as input. Returns true if correctly formatted for bracketing. Otherwise, False.
    .csv formating.
    - the file must not be empty
    - may or may not contain a header row.
    - all rows have 4 values
    - the first val can only contain 'se', 'de', or 'rr'.
    - the second val can only continuious numbers
    - the third val can only contain names.
    - the fourth val can only contain numbers or nothing.
    """
    if os.path.getsize(csv_path) == 0:                              # must not be empty
        return False
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        checked_for_header = False
        for row in csv_reader:
            if not checked_for_header:                              # check for header
                checked_for_header = True
                is_header = True
                for val in row:
                    if val.isdigit():
                        is_header = False
                        break
                if is_header:
                    continue
            if len(row) != 4:                                           # rows have 4 vals
                return False
            if row[0] != 'se' and row[0] != 'de' and row[0] != 'rr':      # col 1 check
                return False
            if not row[1].isdigit():                                     # col 2 check
                return False
            if not re.match(r'^[A-Za-z\s]*$', row[2]):                                    # col 3 check
                return False
            if not row[3].isdigit() and row[3] != ' ' and row[3] != '':                   # col 4 check
                return False
    return True
def get_formatted_data_from_csv(csv_path: str) -> dict:
    """
    Takes a path to a .csv file as input. returns the the data.
    """ 
    data = {'Bracket Types': {}}
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if not row[1].isdigit():        # checking for header
                continue
            else:
                if row[0] not in data['Bracket Types']:                                                         # check if the bracket type is already in the data
                    data['Bracket Types'][row[0]] = {'Bracket Numbers': {}}
                if row[1] not in data['Bracket Types'][row[0]]['Bracket Numbers']:                              # check if the bracket number is already in this bracket type
                    data['Bracket Types'][row[0]]['Bracket Numbers'][row[1]] = {'Seeds': {}}
                if row[3].isdigit():                                                                            # check if they have a seed
                    data['Bracket Types'][row[0]]['Bracket Numbers'][row[1]]['Seeds'][row[3]] = row[2]
                else:                                                                                           # add to unseeded list
                    if 'Un-seeded' not in data['Bracket Types'][row[0]]['Bracket Numbers'][row[1]]['Seeds']:    # is there an unseeded list yet?
                        data['Bracket Types'][row[0]]['Bracket Numbers'][row[1]]['Seeds']['Un-seeded'] = []
                    data['Bracket Types'][row[0]]['Bracket Numbers'][row[1]]['Seeds']['Un-seeded'].append(row[2])        # place the name in the bracket
    return data
def get_fileName_fromPath(path: str) -> str:
    reversed_name = ''
    for i in range(len(path) -1, -1, -1):
        if path[i].isalnum() or path[i] == '.':
            reversed_name += path[i]
        else:
            break
    return reversed_name [:3:-1]
def store_brackets(data: dict, file_name: str) -> None:
    os.chdir('brackets')
    file_num = 0
    file_path = f'{file_name}_{file_num}.json'
    while os.path.exists(file_path):
        file_num += 1
        file_path = f'{file_name}_{file_num}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f'Bracket {file_name}_{file_num} successfully stored at /brackets/{file_path}.')
# generate brackets ------------------------------------------------------------------------------------------------------------------------
def gen_bracket_from_path(path: typing.Optional[str]=None) -> None:
    if path is None:                                                    # They did not provide a path
        path = input('Enter Path to .CSV or 1 to exit: ')
        if path == '1':
            exit()
    path = get_valid_path(path)
    data = get_formatted_data_from_csv(path)
    file_name = get_fileName_fromPath(path)
    store_brackets(data, file_name)
# main program -----------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    args = sys.argv                                                                             # get args
    args_length = len(args)
    if args_length > 3:                                                                         # too many args                                                           
        print(f'Invalid Usage: Too many args. Expected less than 2. Recieved {args_length}')
    elif args_length == 1:                                                                      # no args
        usage_txt()
        exit()       
    arg1_lower = args[1].lower()                                                                # help                       
    if re.match(r'^(h|-h|--h|help|-help|--help)$', arg1_lower): 
        help_txt()
        exit()                   
    elif re.match(r'^(a|-a|--a|about|-about|--about)$', arg1_lower):                               # about                                               
        about_txt()
        exit()
    elif re.match(r'^(cb|-cb|--cb|createbracket|-createbracket|--createbracket)$', arg1_lower):   # create bracket
        if args_length == 3:
            gen_bracket_from_path(args[2])
            exit()
            pass
        else:
            gen_bracket_from_path()
            exit()                                                           
    elif is_valid_path_to_csv(args[1]):                                                              # provided only path
        gen_bracket_from_path(args[1])
        exit()
    else:                                                                                           # no valid arguments
        usage_txt()
        exit()
    
    

    
    