
class BaseResolver:
    def __init__(self):
        pass

    @staticmethod
    def extract_subfields(selection):
        subfield = {selection.name: []}
        for sub_selection in selection.selections:
            if sub_selection.selections:
                subfield[selection.name].append(BaseResolver.extract_subfields(sub_selection))
            else: 
                subfield[selection.name].append(sub_selection.name)
                
        return subfield

    @staticmethod
    def get_requested_fields(query_fields):
        fields = []
        
        for field in query_fields.selected_fields:
            for selection in field.selections:
                if selection.selections:
                    subfield = BaseResolver.extract_subfields(selection)
                    fields.append(subfield)
                else: 
                    fields.append(selection.name)
                    
        return fields