from noapiframe import ElementBase, docDB


class TimelineTemplate(ElementBase):
    """
Defines a template for Timelines. TimelineTemplates are used as an easy way to populate (and update) multiple Kiosks with a Timeline

desc : str
    some helpful description
user_id : str
    creator/owner of the TimelineTemplate
screen_ids : list
    list of Screens used by this TimelineTemplate, this also sets the order of apperance on the Kiosk
presentation : bool
    if True, linked Timelines accept presentation WSS events when displayed

update_timelines()
    writes screen_ids to linked (unlocked) Timelines
    """
    _attrdef = dict(
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        user_id=ElementBase.addAttr(type=str, notnone=True, fk='User'),
        screen_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='Screen'),
        presentation=ElementBase.addAttr(type=bool, default=False, notnone=True)
    )

    def import_pdf(self, pdf_media, prefix='pdf_importer', png_width=1920):
        """
        Converts a PDF (stored as Media type=4) into Screens using the "Background Image" template.

        The PDF is retrieved from S3 via its Media ID, then each page is converted to a PNG image
        (with the specified width), stored in S3 as a Media element (type=0, src_type=1), and wrapped
        in a Screen that references it via the Background Image template's 'image' variable.

        The resulting screen_ids are assigned to this TimelineTemplate and saved.

        pdf_media : str
            Media ID of the PDF file (must be type=4(other) and src_type=1(internal S3))
        prefix : str (default: 'pdf_importer')
            prefix used in the desc of each created Media and Screen, followed by page number
        png_width : int (default: 1920)
            width in pixels for the converted PNG images; height is scaled proportionally

        Returns:
            bool: True on success, False if the "Background Image" ScreenTemplate or PDF Media is not found
        """
        from pdf2image import convert_from_path
        import tempfile
        from elements import Media, Screen, ScreenTemplate
        from helpers.s3 import media_get, media_upload

        screen_ids = []

        # Find the "Background Image" ScreenTemplate
        bg_template = ScreenTemplate()
        fromdb = docDB.search_one('ScreenTemplate', {'name': 'Background Image'})
        if fromdb is None:
            return False
        bg_template._attr = fromdb

        # Look up the PDF Media element by ID
        pdf_media_elem = Media.get(pdf_media)
        if pdf_media_elem['_id'] is None or not pdf_media_elem['type'] == 4 or not pdf_media_elem['src_type'] == 1:
            return False

        with tempfile.TemporaryDirectory() as tmpdir:
            # Download PDF from S3 into memory, then write to temp file
            pdf_bytes = media_get(pdf_media_elem['_id'])
            pdf_path = f'{tmpdir}/source.pdf'
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes.read())

            # Convert each PDF page to a PNG image
            images = convert_from_path(pdf_path, size=(png_width, None))

            for page_num, image in enumerate(images, start=1):
                # Save page as PNG in temp directory
                png_path = f'{tmpdir}/page_{page_num}.png'
                image.save(png_path, 'PNG')

                # Create Media element (type=0: static image, src_type=1: S3 storage)
                media = Media({
                    'desc': f'{prefix}{page_num}',
                    'src': f'page{page_num}.png;image/png',
                    'src_type': 1,
                    'type': 0,
                    'user_id': self['user_id'],
                    'common': False
                })
                media.save()

                # Upload PNG to S3 using the media's _id as the key
                with open(png_path, 'rb') as png_file:
                    media_upload(media['_id'], png_file)

                # Create a Screen for this Media using the Background Image template
                screen = Screen({
                    'template_id': bg_template['_id'],
                    'user_id': self['user_id'],
                    'desc': f'{prefix}{page_num}',
                    'variables': {'image': media['_id']}
                })
                screen.save()

                screen_ids.append(screen['_id'])

        self['screen_ids'] = screen_ids
        self.save()
        return True

    def save_post(self):
        from elements import Timeline
        from helpers.wss import transmit_timelinetemplate_update
        transmit_timelinetemplate_update(self)
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'template_id': self['_id']})]:
            t.save()

    def delete_post(self):
        from elements import Timeline
        from helpers.wss import transmit_timelinetemplate_delete
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'template_id': self['_id']})]:
            t['template_id'] = None
            t.save()
        transmit_timelinetemplate_delete(self)

    def update_timelines(self):
        from elements import Timeline
        result = list()
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'template_id': self['_id']})]:
            if not t.locked():
                t['screen_ids'] = list()
                for s in self['screen_ids']:
                    t['screen_ids'].append(s)
                t.save()
                result.append(t['_id'])
        return result
