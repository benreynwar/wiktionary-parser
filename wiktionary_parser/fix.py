class Fix(object):
    """
    Holds information on a type of repair that can be
    applied to text.

    ``section_type`` is the type of section it can be applied to.

    """
    def __init__(self, slug, description='', section_type=None):
        self.slug = slug
        self.description = description
        self.section_type = section_type
