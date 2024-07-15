import csv


class Read:
    """
    Class to process all files
    """
    def __init__(self):
        self.data = []
        
    def get_list_from(self, file_path):
        """
        Get list from file
        """
        with open(file_path, "r", encoding="utf-8") as our_file:
            if file_path.split('.')[-1].lower() == "csv":
                self.data = csv.reader(our_file)
                next(self.data)
                return self.drop_empty_rows()
               
            for line in our_file:
                self.data.append(list(line.strip().split(',')))
            return self.drop_empty_rows()

    def drop_empty_rows(self):
        """
        Drop all empty rows to save on future processing
        """
        file_list = []

        for line in self.data:
            stripped_row = [value.strip() for value in line]
            if any(stripped_row):
                file_list.append(stripped_row)
        return file_list
