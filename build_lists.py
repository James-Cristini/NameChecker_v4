import string
import sqlite3

def parse_names(names_text):
    #print names_text
    if names_text:
        names_list = [x.strip(string.whitespace) for x in names_text.split("\n") if x.strip(string.whitespace)]
        stripped_names = []

        # Remove extra asterisks and replace instances of brackets with parenthesis then split each line into a separate item for names_list
        new_text = ""
        for x in range(len(names_text)-1) :
            if names_text[x] == "*" and names_text[x+1] not in string.letters :
                pass
            else :
                new_text += names_text[x]
        new_text += names_text[-1]

        new_text = new_text.replace("[", "(").replace("]", ")").replace("*", "(").split("\n")

        for x in new_text :
            # Break each line up into its major components [Names, pronunciation, rationale, etc.]
            line_components = x.split("(")
            # Break the first component of line_components (should be all names potentially separated by a '/')
            names_on_line = line_components[0].split("/")
            # Add each name to the list of stripped names to be returned
            stripped_names += [x.strip(string.whitespace) for x in names_on_line if x.strip(string.whitespace)]
            #stripped_names.sort()

        return stripped_names, names_list
    else:
        return [], []

def build_project_avoids(avoid_list):
    # Create a new dictionary that will hold project avoids split up into its proper -fix category
    project_avoids = {
        "prefix" : [],
        "infix" : [], #infix is stored in "anywhere" for project avoids
        "suffix" : [],
        "problems" : [],
        "anywhere" : []
    }
    # Determine if avoids are prefix/infix/suffix and build the project_avoids dictionary accordingly
    for avoid in avoid_list:

        if "," in avoid :
            avoid_line = avoid.split(",")
            avoid = avoid_line[0].strip(string.whitespace)
            for x in range(1, len(avoid_line)):
                avoid_list.append(avoid_line[x].strip(string.whitespace))

        if "(" in avoid:
            line = avoid.split("(")
            avoid = line[0].strip(string.whitespace)
        if "-" in avoid and '"' in avoid:
            avoid = avoid.strip('"').strip(string.whitespace)
        elif "-" not in avoid and '"' not in avoid and " " not in avoid:
            avoid = ('"' + avoid + '"')

        if " " not in avoid.strip(string.whitespace):
        # Check for Infix first, if it starts and ends with a - or " it is an infix
        # Infixes are stored as "anywhere" for project avoids
            if avoid[0] == '"' and avoid[-1] == '"' or avoid[0] == '-' and avoid[-1] == '-':
                project_avoids["anywhere"].append(avoid.strip("-").strip('"'))

            # If it only ends in with a -, it's a prefix
            elif avoid[-1] == "-":
                project_avoids["prefix"].append(avoid.strip("-").strip('"'))

            # If it starts with a -, it's a suffix
            elif avoid[0] == "-":
                project_avoids["suffix"].append(avoid.strip("-").strip('"'))

            else:
                #print "Problem with:", avoid
                if  "reformat" not in avoid.lower():
                    project_avoids["problems"].append("Reformat " + avoid)
                else:
                    project_avoids["problems"].append(avoid)
        else:
            #print "Problem with:", avoid
            if  "reformat" not in avoid.lower():
                project_avoids["problems"].append("Reformat " + avoid)
            else:
                project_avoids["problems"].append(avoid)
    # Return the full dictionary
    return project_avoids

def write_avoids(project_avoids, internal_names, competitor_names) :
    with open("avoids.txt", "w") as f:
        line = ""
        for x in project_avoids:
            line = "Project: "
            line += ",".join(project_avoids)
        f.write(line + "\n")

        line = ""
        for x in internal_names:
            line = "Internal: "
            line += ",".join(internal_names)
        f.write(line + "\n")

        line = ""
        for x in competitor_names:
            line = "Competitor: "
            line += ",".join(competitor_names)
        f.write(line + "\n")

if __name__ == '__main__':
    pass
