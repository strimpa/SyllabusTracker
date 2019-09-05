from SyllabusTrackerApp.models import Rating

def ColourFromAverage(average):
    progress = (average / 3.0 * 255.0)
    return ("rgb("+str(255 - progress)+","+str(progress)+",0)")

class ExerciseStudentSummary():
    def __init__(self, name):
        self.name = name
        self.students_ratings = {}
        self.rating_average = 0
    def __str__(self):
        return self.name+"average:"+str(self.rating_average)

class DisplayLeaf():
    def __init__(self, name, depth, group=None):
        self.name = name
        self.id = 0
        self.children = []
        self.exercises = []
        self.parent_leaf = None
        self.show_in_hierarchy = False
        self.list_order_index = 0
        self.chapter = ""
        self.depth = depth
        self.description = "None"
        self.average = 0.0
        self.colour = "blue"
        if group!=None:
            self.name = group.name
            self.id = group.id
            self.show_in_hierarchy = group.show_in_hierarchy
            self.list_order_index = group.list_order_index
            self.description = group.description

    def __str__(self):
        return "DisplayLeaf:"+self.name+": "+str(self.depth)
        
    def print_hier(self, depth):
        output = ""
        for i in range(depth):
            output += ("   ")
        output += self.chapter
        output += " '"+self.name+"'"
        output += " '"+self.description+"'"
        output += ", "+str(self.depth)
        print(output)
        for c in self.children:
            c.print_hier(depth+1)
        for c, r in self.exercises:
            try:
                print("- "+c.name+":"+str(depth+1))
            except:
                pass

    def enumerate_hier(self, depth, chapter_string, chapter):
        self.chapter += chapter_string
        # don't enumerate display root
        if depth>0 and self.show_in_hierarchy:
            if len(chapter_string)>0:
                self.chapter += "."
            self.chapter += str(chapter)

        child_chapter_index = 1
        for c in self.children:
            c.enumerate_hier(depth+1, self.chapter, child_chapter_index)
            child_chapter_index += 1

        num_ratings = 0
        for ex, rating in self.exercises:
            if rating:
                if isinstance(rating, ExerciseStudentSummary):
                    self.average += rating.rating_average
                else:
                    self.average += Rating.PROFICIENCY_TOKENS.index(rating.proficiency)
                num_ratings += 1
        if num_ratings>0:
            self.average /= num_ratings
            self.colour = ColourFromAverage(self.average)

    def find_leaf(self, leaf_name):
        if self.name == leaf_name:
            return self
        for child in self.children:
            found = child.find_leaf(leaf_name)
            if found != None:
                return found
        return None

    def find_or_create_leaf(group, group_root, root_depth):
        display_leaf = group_root.find_leaf(group.name)
        if display_leaf == None:
            display_leaf = DisplayLeaf(group.name, root_depth, group=group)
            if group.parent_group != None:
                display_leaf.parent_leaf = DisplayLeaf.find_or_create_leaf(group.parent_group, group_root, root_depth)
                #only increase the depth if the leaf is shown in hierarchy
                if display_leaf.parent_leaf.show_in_hierarchy:
                    display_leaf.depth = display_leaf.parent_leaf.depth+1
            else:
                display_leaf.parent_leaf = group_root

        if not display_leaf in display_leaf.parent_leaf.children:
            curr_index = 0
            for c in display_leaf.parent_leaf.children:
                if c.list_order_index>=display_leaf.list_order_index:
                    break
                curr_index+=1
            display_leaf.parent_leaf.children.insert(curr_index, display_leaf)
        return display_leaf
