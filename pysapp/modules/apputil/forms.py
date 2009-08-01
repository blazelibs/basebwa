import datetime
from pysmvt import appimportauto
appimportauto('forms', 'Form')

class TestForm(Form):
    def __init__(self, static):
        Form.__init__(self, 'testform', static=static)

        
        el = self.add_button('button', 'Button', defaultval='PushMe')
        el = self.add_checkbox('checkbox', 'Checkbox')
        el = self.add_file('file', 'File')
        el.add_note('a note that has a lot of text in it Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent justo massa, porttitor id malesuada in, ultricies ac odio. Morbi sit amet sapien a nisl tincidunt luctus ultricies euismod erat. Integer tempor, tortor id ornare iaculis, nibh nisi imperdiet eros, ut tristique turpis eros ac ligula.')
        el = self.add_hidden('hidden', defaultval='my hidden val')
        el = self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.add_text('text', 'Text')
        el.add_note('a note that has a lot of text in it Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent justo massa, porttitor id malesuada in, ultricies ac odio. Morbi sit amet sapien a nisl tincidunt luctus ultricies euismod erat. Integer tempor, tortor id ornare iaculis, nibh nisi imperdiet eros, ut tristique turpis eros ac ligula.')
        el.add_note('an <strong>HTML</strong> note', False)
        el = self.add_text('nolabel', defaultval='No Label', required=True)
        el.add_note('a note')
        el = self.add_password('password', 'Password', required=True)
        el = self.add_confirm('confirm', 'Confirm Password', match='password')
        el.add_note('confirm characters for password field are automatically masked')
        el = self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        el.add_note('note the automatic conversion from datetime object')
        emel = self.add_email('email', 'Email')
        el = self.add_confirm('confirmeml', 'Confirm Email', match=emel)
        el.add_note('note you can confirm with the name of the field or the element object')
        el.add_note('when not confirming password field, characters are not masked')
        el = self.add_time('time', 'Time')
        el = self.add_url('url', 'URL')
        options = [('1', 'one'), ('2','two')]
        el = self.add_select('select', options, 'Select')
        el = self.add_mselect('mselect', options, 'Multi Select')
        el = self.add_textarea('textarea', 'Text Area')
        el = self.add_passthru('passthru', 123)
        el = self.add_fixed('fixed', 'Fixed', 'fixed val')
        el = self.add_static('static', 'Static', 'static val')
        el = self.add_header('header', 'header')
        
        # want a header for div wrapping only, header element should not actually render
        el = self.add_header('header-for-div-wrap-only')
        el = self.add_text('hfdwo-t1', 'Text1', required=True)
        el = self.add_text('hfdwo-t2', 'Text2', required=True)
        
        # test header with blank text
        el = self.add_header('header-blank-text', '')
        el = self.add_text('hbt-t1', 'Text1')
        el = self.add_text('hbt-t2', 'Text2')
        
        # test element group with class attribute
        sg = self.add_elgroup('group')
        sg.add_text('ingroup1', 'ingroup1')
        sg.add_text('ingroup2', 'ingroup2')
        
        self.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.add_radio('r2', 'r2', defaultval='car', group='rgroup')
        
        sg = self.add_elgroup('submit-group', class_='submit-only')
        el = sg.add_reset('reset')
        el = sg.add_submit('submit')
        el = sg.add_cancel('cancel')
