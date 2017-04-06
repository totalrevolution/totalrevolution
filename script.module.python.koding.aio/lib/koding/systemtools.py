# -*- coding: utf-8 -*-

# script.module.python.koding.aio
# Python Koding AIO (c) by whufclee (info@totalrevolution.tv)

# Python Koding AIO is licensed under a
# Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.

# You should have received a copy of the license along with this
# work. If not, see http://creativecommons.org/licenses/by-nc-nd/4.0.

# IMPORTANT: If you choose to use the special noobsandnerds features which hook into their server
# please make sure you give approptiate credit in your add-on description (noobsandnerds.com)
# 
# Please make sure you've read and understood the license, this code can NOT be used commercially
# and it can NOT be modified and redistributed. Thank you.

import datetime
import os
import sys
import shutil
import xbmc
import xbmcgui

import filetools

dialog = xbmcgui.Dialog()
#----------------------------------------------------------------
def Check_Deps(addon_path, depfiles = []):
    import re
    from filetools import Text_File
    try:
        readxml = Text_File(os.path.join(addon_path,'addon.xml'),'r')
        dmatch   = re.compile('import addon="(.+?)"').findall(readxml)
        for requires in dmatch:
            if not 'xbmc.python' in requires and not requires in depfiles:
                depfiles.append(requires)
    except:
        pass
    return depfiles
#----------------------------------------------------------------
# TUTORIAL #
def Cleanup_String(my_string):
    """
Clean a string, removes whitespaces and common buggy formatting when pulling from websites

CODE: Cleanup_String(my_string)

    AVAILABLE PARAMS:
        
        (*) my_string   -  This is the main text you want cleaned up.
        
EXAMPLE CODE:
current_text = '" This is a string of text which should be cleaned up   /'
clean_text = koding.Cleanup_String(current_text)
xbmc.log(clean_text)
dialog.ok('CLEAN', clean_text)
~"""
    import urllib
    bad_chars = ['/','\\',':',';','"',"'"]

    try:
        my_string = my_string.encode('utf8')
    except:
        pass
    
    my_string = urllib.unquote_plus(my_string)
    my_string = my_string.replace('&amp;','&')
    
    if len(my_string) > 4:
        if my_string[-4] == '.':
            my_string = my_string[:-4]
    
    my_string = my_string.strip()

    while my_string[0] in bad_chars or my_string[-1] in bad_chars:
        if my_string[-1] in bad_chars:
            my_string = my_string[:-1]
        if my_string[0] in bad_chars:
            my_string = my_string[1:]
        my_string = my_string.strip()

    return my_string
#----------------------------------------------------------------
# TUTORIAL #
def Colour_Text(text, colour1='dodgerblue',colour2='white'):
    """
Capitalize a string and make the first colour of each string blue and the rest of text white
That's the default colours but you can change to whatever colours you want.

CODE: Colour_Text(text, [color1, color2])

    AVAILABLE PARAMS:
        
        (*) text   -  This is the main text you want to change

        colour1 -  This is optional and is set as dodgerblue by default.
        This is the first letter of each word in the string

        colour2 -  This is optional and is set as white by default. 
        This is the colour of the text

IMPORTANT: I use the Queens English so please note the word "colour" has a 'u' in it!

EXAMPLE CODE:
current_text = 'This is a string of text which should be changed to dodgerblue and white with every first letter capitalised'
mytext = koding.Colour_Text(text=current_text, colour1='dodgerblue', colour2='white')
xbmc.log(current_text)
xbmc.log(mytext)
dialog.ok('CURRENT TEXT', current_text)
dialog.ok('NEW TEXT', mytext)~"""

    if text.startswith('[COLOR') and text.endswith('/COLOR]'):
        return text

    colour_clean = 0

    if ' ' in text:
        newname = ''
        text = text.split(' ')
        for item in text:
            if len(item)==1 and item == '&':
                newname += ' &'
            if '[/COLOR]' in item:
                newname += ' '+item
            elif not item.startswith('[COLOR=') and not colour_clean:
                if item.startswith('(') or item.startswith('['):
                    newname += '[COLOR=yellow] '+item
                    colour_clean = 1
                else:
                    if item.isupper():
                        newname += '[COLOR=%s] %s[/COLOR]' % (colour1, item)
                    else:
                        try:
                            newname += '[COLOR=%s] %s[/COLOR][COLOR=%s]%s[/COLOR]' % (colour1, item[0].upper(), colour2, item[1:])
                        except:
                            try:
                                newname += '[COLOR=%s] %s[/COLOR][COLOR=%s][/COLOR]' % (colour1, item[0], colour2, item[1:])
                            except:
                                pass
            

            elif item.endswith(')') or item.endswith(']'):
                newname += ' '+item+'[/COLOR]'
                colour_clean = 0

            else:
                newname += ' '+item

    else:
        if text[0] == '(':
            newname = '[COLOR=%s]%s[/COLOR][COLOR=%s]%s[/COLOR][COLOR=%s]%s[/COLOR]' % (colour2, text[0], colour1, text[1].upper(), colour2, text[2:])
        else:
            newname = '[COLOR=%s]%s[/COLOR][COLOR=%s]%s[/COLOR]' % (colour1, text[0], colour2, text[1:])

    success = 0
    while success != 1:
        if newname.startswith(' '):
            newname = newname[1:]
        success = 1
    if newname.startswith('[COLOR=%s] ' % colour1):
        newname = '[COLOR=%s]%s' % (colour1, newname[19:])

    return newname
#----------------------------------------------------------------
# TUTORIAL #
def Cleanup_Textures(frequency=14,use_count=10):
    """
This will check for any cached artwork and wipe if it's not been accessed more than 10 times in the past x amount of days.

CODE: Cleanup_Textures([frequency, use_count])

    AVAILABLE PARAMS:
        
        frequency  -  This is an optional integer, be default it checks for any
        images not accessed in 14 days but you can use any amount of days here.

        use_count   -  This is an optional integer, be default it checks for any
        images not accessed more than 10 times. If you want to be more ruthless
        and remove all images not accessed in the past x amount of days then set this very high.

EXAMPLE CODE:
dialog.ok('Clean Textures','We are going to clear any old cached images not accessed at least 10 times in the past 5 days')
koding.Cleanup_Textures(frequency=5)
~"""
    try: from sqlite3 import dbapi2 as database
    except: from pysqlite2 import dbapi2 as database

    db   = filetools.DB_Path_Check('Textures')
    xbmc.log('### DB_PATH: %s' % db)
    conn = database.connect(db, timeout = 10, detect_types=database.PARSE_DECLTYPES, check_same_thread = False)
    conn.row_factory = database.Row
    c = conn.cursor()

    # Set paramaters to check in db, cull = the datetime (we've set it to 14 days) and useCount is the amount of times the file has been accessed
    cull     = datetime.datetime.today() - datetime.timedelta(days = frequency)

    # Create an array to store paths for images and ids for database
    ids    = []
    images = []

    c.execute("SELECT idtexture FROM sizes WHERE usecount < ? AND lastusetime < ?", (use_count, str(cull)))

    for row in c:
        ids.append(row["idtexture"])

    for id in ids:
        c.execute("SELECT cachedurl FROM texture WHERE id = ?", (id,))
        for row in c:
            images.append(row["cachedurl"])


# Clean up database
    for id in ids:       
        c.execute("DELETE FROM sizes   WHERE idtexture = ?", (id,))
        c.execute("DELETE FROM texture WHERE id        = ?", (id,))

    c.execute("VACUUM")
    conn.commit()
    c.close()

    xbmc.log("### Automatic Cache Removal: %d Old Textures removed" % len(images))

# Delete files
    thumbfolder = xbmc.translatePath('special://home/userdata/Thumbnails')
    for image in images:
        path = os.path.join(thumbfolder, image)
        try:
            os.remove(path)
        except:
            kodi.log(Last_Error())
#----------------------------------------------------------------
# TUTORIAL #
def Clear_Data(addonid):
    """
If you want to offer the option to clear the cookie data then you can add the
following code in your settings.xml. This will wipe the cookies folder - could
be useful if things like the initial run code sent back from server alters or
the base urls have changed.

<setting id="clear_data"    label="Re-check Server" type="action"   action="RunScript(special://home/addons/script.module.python.koding.aio/lib/koding/__init__.py,clear_data,your.plugin.id)"  option="close"  visible="true"/>
~"""
    root_path = os.path.join(xbmc.translatePath('special://profile/addon_data'),addonid)
    
    try:
        xbmc.log('data cleared from: %s' % addonid)
        shutil.rmtree(os.path.join(root_path, 'cookies'))
        return True
    except:
        xbmc.log('failed to clear data from: %s' % addonid)
        return False
#----------------------------------------------------------------
# TUTORIAL #
def Dependency_Check(addon_id = 'all', recursive = False):
    """
This will return a list of all dependencies required by an add-on.
This information is grabbed directly from the currently installed addon.xml for that id.

CODE:  Dependency_Check([addon_id, recursive])

AVAILABLE PARAMS:

    addon_id  -  This is optional, if not set it will return a list of every
    dependency required from all installed add-ons. If you only want to
    return results of one particular add-on then send through the id.

    recursive  -  By default this is set to False but if set to true and you
    also send through an individual addon_id it will return all dependencies
    required for that addon id AND the dependencies of the dependencies.

EXAMPLE CODE:
current_id = xbmcaddon.Addon().getAddonInfo('id')
dependencies = koding.Dependency_Check(addon_id=current_id, recursive=True)
clean_text = ''
for item in dependencies:
    clean_text += item+'\n'
koding.Text_Box('Modules required for %s'%current_id,clean_text)
~"""
    import xbmcaddon
    import re
    from filetools import Text_File
    ADDONS = xbmc.translatePath('special://home/addons')
    depfiles = []

    if addon_id == 'all':
        for name in os.listdir(ADDONS):
            if name != 'packages':
                try:
                    addon_path = os.path.join(ADDONS,name)
                    depfiles = Check_Deps(addon_path)
                except:
                    pass
    else:
        try:
            addon_path = xbmcaddon.Addon(id=addon_id).getAddonInfo('path')
        except:
            addon_path = os.path.join(ADDONS,addon_id)

        depfiles = Check_Deps(addon_path)

        if recursive:
            dep_path = None
            for item in depfiles:
                try:
                    dep_path = xbmcaddon.Addon(id=item).getAddonInfo('path')
                except:
                    dep_path = os.path.join(ADDONS,item)

            if dep_path:
                depfiles = Check_Deps(dep_path)

    return depfiles
#----------------------------------------------------------------
# TUTORIAL #
def End_Path(path):
    """
Split the path at every '/' and return the final file/folder name.
If your path uses backslashes rather than forward slashes it will use
that as the separator.

CODE:  End_Path(path)

AVAILABLE PARAMS:

    path  -  This is the path where you want to grab the end item name.

EXAMPLE CODE:
addons_path = xbmc.translatePath('special://home/addons')
file_name = koding.End_Path(path=addons_path)
dialog.ok('ADDONS FOLDER','Path checked:',addons_path,'Folder Name: [COLOR=dodgerblue]%s[/COLOR]'%file_name)
file_path = xbmc.translatePath('special://home/addons/script.module.python.koding.aio/addon.xml')
file_name = koding.End_Path(path=file_path)
dialog.ok('FILE NAME','Path checked:',file_path,'File Name: [COLOR=dodgerblue]%s[/COLOR]'%file_name)
~"""
    if '/' in path:
        path_array = path.split('/')
        if path_array[-1] == '':
            path_array.pop()
    elif '\\' in path:
        path_array = path.split('\\')
        if path_array[-1] == '':
            path_array.pop()
    else:
        return path
    return path_array[-1]
#----------------------------------------------------------------
# TUTORIAL #
def Get_Addon_ID(folder):
    """
If you know the folder name of an add-on but want to find out the
addon id (it may not necessarily be the same as folder name) then
you can use this function. Even if the add-on isn't enabled on the
system this will regex out the add-on id.

CODE:  Get_Addon_ID(folder)

AVAILABLE PARAMS:
    
    folder  -  This is folder name of the add-on. Just the name not the path.

EXAMPLE CODE:
my_id = koding.Get_Addon_ID(folder='script.module.python.koding.aio')
dialog.ok('ADDON ID','The add-on id found is:','[COLOR=dodgerblue]%s[/COLOR]'%my_id)
~"""
    from filetools import Text_File
    import re
    ADDONS = xbmc.translatePath('special://home/addons')
    xmlpath = os.path.join(ADDONS, folder, 'addon.xml')
    if os.path.exists(xmlpath):
        contents = Text_File(xmlpath,'r')
        addon_id = re.compile('id="(.+?)"').findall(contents)
        addon_id = addon_id[0] if (len(addon_id) > 0) else ''
        return addon_id
#----------------------------------------------------------------
# TUTORIAL #
def Grab_Log(log_type = 'std', formatting = 'original', sort_order = 'reverse'):
    """
This will grab the log file contents, works on all systems even forked kodi.

CODE:  Grab_Log([log_type, formatting, sort_order])

AVAILABLE PARAMS:
    
    log_type    -  This is optional, if not set you will get the current log.
    If you would prefer the old log set this to 'old'

    formatting  -  By default you'll just get a default log but you can set
    this to 'warnings', 'notices', 'errors' to filter by only those error types.
    Notices will return in blue, warnings in gold and errors in red.
    You can use as many of the formatting values as you want, just separate by an
    underscore such as 'warnings_errors'. If using anything other than the
    default in here your log will returned in order of newest log activity first
    (reversed order). You can also use 'clean' as an option and that will just
    return the full log but with clean text formatting and in reverse order.

    sort_order   -  This will only work if you've sent through an argument other
    than 'original' for the formatting. By default the log will be shown in
    'reverse' order but you can set this to 'original' if you prefer ascending
    timestamp ordering like a normal log.

EXAMPLE CODE:
my_log = koding.Grab_Log()
dialog.ok('KODI LOG LOOP','Press OK to see various logging options, every 5 seconds it will show a new log style.')
koding.Text_Box('CURRENT LOG FILE (ORIGINAL)',my_log)
xbmc.sleep(5000)
my_log = koding.Grab_Log(formatting='clean', sort_order='reverse')
koding.Text_Box('CURRENT LOG FILE (clean in reverse order)',my_log)
xbmc.sleep(5000)
my_log = koding.Grab_Log(formatting='errors_warnings', sort_order='reverse')
koding.Text_Box('CURRENT LOG FILE (erros & warnings only - reversed)',my_log)
xbmc.sleep(5000)
old_log = koding.Grab_Log(log_type='old')
koding.Text_Box('OLD LOG FILE',old_log)
~"""
    from filetools import Text_File
    log_path    = xbmc.translatePath('special://logpath/')
    logfilepath = os.listdir(log_path)
    finalfile   = 0
    for item in logfilepath:
        cont = False
        if item.endswith('.log') and not item.endswith('.old.log') and log_type == 'std':
            mylog        = os.path.join(log_path,item)
            cont = True
        elif item.endswith('.old.log') and log_type == 'old':
            mylog        = os.path.join(log_path,item)
            cont = True
        if cont:
            lastmodified = os.path.getmtime(mylog)
            if lastmodified>finalfile:
                finalfile = lastmodified
                logfile   = mylog
    
    logtext = Text_File(logfile, 'r')

    if formatting != 'original':
        logtext_final = ''

        with open(logfile) as f:
            log_array = f.readlines()
        log_array = [line.strip() for line in log_array]
        
        if sort_order == 'reverse':
            log_array = reversed(log_array)

        for line in log_array:
            if ('warnings' in formatting or 'clean' in formatting) and 'WARNING:' in line:
                logtext_final += line.replace('WARNING:', '[COLOR=gold]WARNING:[/COLOR]')+'\n'
            if ('errors' in formatting or 'clean' in formatting) and 'ERROR:' in line:
                logtext_final += line.replace('ERROR:', '[COLOR=red]ERROR:[/COLOR]')+'\n'
            if ('notices' in formatting or 'clean' in formatting) and 'NOTICE:' in line:
                logtext_final += line.replace('NOTICE:', '[COLOR=dodgerblue]NOTICE:[/COLOR]')+'\n'

        logtext = logtext_final

    return logtext
#----------------------------------------------------------------
# TUTORIAL #
def ID_Generator(size=15):
    """
This will generate a random string made up of uppercase & lowercase ASCII
characters and digits - it does not contain special characters.

CODE:  ID_Generator([size])
size is an optional paramater.

AVAILABLE PARAMS:

    size - just send through an integer, this is the length of the string you'll get returned.
    So if you want a password generated that's 20 characters long just use ID_Generator(20). The default is 15.

EXAMPLE CODE:
my_password = koding.ID_Generator(20)
dialog.ok('ID GENERATOR','Password generated:', '', '[COLOR=dodgerblue]%s[/COLOR]' % my_password)
~"""
    import string
    import random

    chars=string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(size))
#----------------------------------------------------------------
# TUTORIAL #
def Installed_Addons(types='unknown', content ='unknown', properties = ''):
    """
This will send back a list of currently installed add-ons on the system.
All the three paramaters you can send through to this function are optional,
by default (without any params) this function will return a dictionary of all
installed add-ons. The dictionary will contain "addonid" and "type" e.g. 'xbmc.python.pluginsource'.

CODE: Installed_Addons([types, content, properties]):

AVAILABLE PARAMS:

    types       -  If you only want to retrieve details for specific types of add-ons
    then use this filter. Unfortunately only one type can be filtered at a time,
    it is not yet possible to filter multiple types all in one go. Please check
    the official wiki for the add-on types avaialble but here is an example if
    you only wanted to show installed repositories: koding.Installed_Addons(types='xbmc.addon.repository')

    content     -  Just as above unfortunately only one content type can be filtered
    at a time, you can filter by video,audio,image and executable. If you want to
    only return installed add-ons which appear in the video add-ons section you
    would use this: koding.Installed_Addons(content='video')

    properties  -  By default a dictionary containing "addonid" and "type" will be
    returned for all found add-ons meeting your criteria. However you can add any
    properties in here available in the add-on xml (check official Wiki for properties
    available). Unlike the above two options you can choose to add multiple properties
    to your dictionary, see example below:
    koding.Installed_Addons(properties='name,thumbnail,description')


EXAMPLE CODE:
my_video_plugins = koding.Installed_Addons(types='xbmc.python.pluginsource', content='video', properties='name')
final_string = ''
for item in my_video_plugins:
    final_string += 'ID: %s | Name: %s\n'%(item["addonid"], item["name"])
koding.Text_Box('LIST OF VIDEO PLUGINS',final_string)
~"""
    try:    import simplejson as json
    except: import json

    addon_dict = []
    if properties != '':
        properties = properties.replace(' ','')
        properties = '"%s"' % properties
        properties = properties.replace(',','","')
    
    query = '{"jsonrpc":"2.0", "method":"Addons.GetAddons","params":{"properties":[%s],"enabled":"all","type":"%s","content":"%s"}, "id":1}' % (properties,types,content)
    response = xbmc.executeJSONRPC(query)
    data = json.loads(response)
    if "result" in data:
        addon_dict = data["result"]["addons"]
    return addon_dict
#----------------------------------------------------------------
# TUTORIAL #
def Last_Error():
    """
Return details of the last error produced, perfect for try/except statements

CODE: Last_Error()

EXAMPLE CODE:
try:
    xbmc.log(this_should_error)
except:
koding.Text_Box('ERROR MESSAGE',Last_Error())
~"""

    import traceback
    error = traceback.format_exc()
    return error
#----------------------------------------------------------------
# TUTORIAL #
def Open_Settings(addon_id=sys.argv[0], stop_script = True):
    """
By default this will open the current add-on settings but if you pass through an addon_id it will open the settings for that add-on.

CODE: Open_Settings([addon_id, stop_script])

AVAILABLE PARAMS:

    addon_id    - This optional, it can be any any installed add-on id. If nothing is passed
    through the current add-on settings will be opened.

    stop_script - By default this is set to True, as soon as the addon settings are opened
    the current script will stop running. If you pass through as False then the script will
    continue running in the background - opening settings does not pause a script, Kodi just
    see's it as another window being opened.

EXAMPLE CODE:
koding.Open_Settings('plugin.video.youtube')
~"""
    import xbmcaddon

    ADDON = xbmcaddon.Addon(id=addon_id)
    ADDON.openSettings(addon_id)
    if stop_script:
        try:
            sys.exit()
        except:
            pass
#----------------------------------------------------------------
# TUTORIAL #
def Show_Busy(status=True):
    """
This will show/hide a "working" symbol.

CODE: Show_Busy(True)

AVAILABLE PARAMS:

    status - This optional, by default it's True which means the "working" symbol appears. False will disable.

EXAMPLE CODE:
dialog.ok('BUSY SYMBOL','Press OK to show a busy dialog which restricts any user interaction. We have added a sleep of 5 seconds at which point it will disable.')
koding.Show_Busy()
xbmc.sleep(5000)
koding.Show_Busy(False)
~"""
    if status:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
    else:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
#----------------------------------------------------------------
# TUTORIAL #
def Set_Setting(setting_type, setting, value = ''):
    """
Use this to set built-in kodi settings via JSON or set skin settings. The value paramater is only required for JSON and string commands. Available options are below:

CODE: koding.Set_Setting(setting, setting_type, [value])

AVAILABLE PARAMS:
    
    setting_type - The type of setting type you want to change, available types are:

        string (sets a skin string, requires a value)
        bool_true (sets a skin boolean to true, no value required)
        bool_false (sets a skin boolean to false, no value required)
        (!) kodi_setting (sets values found in guisettings.xml)
        (!) addon_enable (enables/disables an addon. setting = addon_id, value = true/false)
        (!) json (WIP - setitng = method, value = params, see documentation on JSON-RPC API here: http://kodi.wiki/view/JSON-RPC_API)

        (!) = These will return True or False if successful

setting - This is the name of the setting you want to change, it could be a setting from the kodi settings or a skin based setting.

value: This is the value you want to change the setting to.


EXAMPLE CODE:
koding.Set_Setting('kodi_setting', 'lookandfeel.enablerssfeeds', 'false')
~"""
    try:    import simplejson as json
    except: import json

    try:

# If the setting_type is kodi_setting we run the command to set the relevant values in guisettings.xml
        if setting_type == 'kodi_setting':
            setting = '"%s"' % setting
            value = '"%s"' % value

            query = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":%s,"value":%s}, "id":1}' % (setting, value)
            response = xbmc.executeJSONRPC(query)

            if 'error' in str(response):
                query = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":%s,"value":%s}, "id":1}' % (setting, value.replace('"',''))
                response = xbmc.executeJSONRPC(query)
                if 'error' in str(response):
                    xbmc.log('### Error With Setting: %s' % response, 2)
                    return False
                else:
                    return True
            else:
                return True

# Set a skin string to <value>
        elif setting_type == 'string':
            xbmc.executebuiltin('Skin.SetString(%s,%s)' % (setting, value))

# Set a skin setting to true
        elif setting_type == 'bool_true':
            xbmc.executebuiltin('Skin.SetBool(%s)' % setting)

# Set a skin setting to false
        elif setting_type == 'bool_false':
            xbmc.executebuiltin('Skin.Reset(%s)' % setting)

# If we're enabling/disabling an addon        
        elif setting_type == 'addon_enable':
            xbmc.executebuiltin('UpdateLocalAddons')
            xbmc.sleep(500)
            query = '{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled","params":{"addonid":"%s", "enabled":%s}, "id":1}' % (setting, value)
            response = xbmc.executeJSONRPC(query)
            if 'error' in str(response):
                xbmc.log('### Error in json: %s'%query,2)
                xbmc.log('^ %s' % response, 2)
                return False
            else:
                return True

# If it's none of the above then it must be a json command so we use the setting_type as the method in json
        elif setting_type == 'json':
            query = '{"jsonrpc":"2.0", "method":"%s","params":{%s}, "id":1}' % (setting, value)
            response = xbmc.executeJSONRPC(query)
            if 'error' in str(response):
                xbmc.log('### Error With Setting: %s' % response)
                return False
            else:
                return True

    except Exception as e:
        xbmc.log(Last_Error())
        xbmc.log(str(e))
#----------------------------------------------------------------
# TUTORIAL #
def Timestamp(mode = 'integer'):
    """
This will return the timestamp in various formats. By default it returns as "integer" mode but other options are listed below:

CODE: koding.Timestamp(mode)
mode is optional, by default it's set as integer

AVAILABLE VALUES:

    'integer' -  An integer which is nice and easy to work with in Python (especially for
    finding out human readable diffs). The format returned is [year][month][day][hour][minutes][seconds]. 
    
    'epoch'   -  Unix Epoch format (calculated in seconds passed since 12:00 1st Jan 1970).

    'clean'   -  A clean user friendly time format: Tue Jan 13 10:17:09 2009

EXAMPLE CODE:
integer_time = koding.Timestamp('integer')
epoch_time = koding.Timestamp('epoch')
clean_time = koding.Timestamp('clean')
dialog.ok('CURRENT TIME','Integer: %s' % integer_time, 'Epoch: %s' % epoch_time, 'Clean: %s' % clean_time)
~"""
    import time
    now = time.time()
    if mode == 'epoch':
        return now
    
    localtime = time.localtime(now)
    if mode == 'integer':
        return time.strftime('%Y%m%d%H%M%S', localtime)

    if mode == 'clean':
        return time.asctime(localtime)
#----------------------------------------------------------------
# TUTORIAL #
def Update_Addons(force='refresh', skip=[], addon_paths=[]):
    """
Get Kodi to re-check for any newly installed add-ons and perform
a forced update on the repos. As of Kodi 17 you can no longer simply
extract a zip to the addons folder and perform an update command,
instead you now need to manually enable each add-on via JSON-RPC.
However that can be done via this command, see below:

CODE: koding.Update_Addons([force, skip, addon_paths])

AVAILABLE PARAMS:

    force      -  By default this is set to 'refresh' which will just
    check for new add-ons and force refresh the repositories. There are
    however 2 other modes you can use:
      
       'new': this will check for any newly extracted addon folders
       and will only enable those newly found items.

       'all': this will loop through ALL add-on folders attempting
       to enable them all.

    skip       -  If there are any add-ons you don't want enabling you
    can send through a list of id's here and they'll be skipped.

    addon_paths  -  leave force as the default of 'refresh' and send
    through a list of addon PATHS. This will then ONLY enable these
    add-ons and their dependencies.

EXAMPLE CODE:
dialog.ok('ADD NEW FOLDERS','Manually copy over some add-ons into your setup then click OK to continue. They should then all be populated and enabled on the system.')
koding.Update_Addons(force='all')
~"""
    import re
    from __init__ import dolog
    from filetools import Text_File

    disabled      = []
    installed     = []
    enable_list   = []
    final_enabled = []
    exclude_list  = ['xbmc.core', 'xbmc.metadata', 'kodi.resource', 'xbmc.addon', 'script.module.metahandler']
    ADDONS        = xbmc.translatePath('special://home/addons')

    if force == 'new':
# Grab list of installed addons and add paths to list
        addon_list = Installed_Addons(properties = 'path')
        for item in addon_list:
            installed.append(item["path"])

# Grab list of addon dirs and add to temp list if not in previous list
        for item in os.listdir(ADDONS):
            path = os.path.join(ADDONS,item)
            if os.path.isdir(path) and not path in installed:
                disabled.append(path)

# Go through the newly found add-ons and grab the addon id's adding to a list
        for item in disabled:
            xmlpath = os.path.join(item,'addon.xml')
            if os.path.exists(xmlpath):
                contents = Text_File(xmlpath,'r')
                addon_id = re.compile('id="(.+?)"').findall(contents)
                addon_id = addon_id[0] if (len(addon_id) > 0) else ''
                if addon_id != '' and addon_id != None:
                    enable_list.append(addon_id)

# Now we have a list of new add-ons we can update addons
    xbmc.executebuiltin('UpdateLocalAddons')

    if force == 'all':
        ADDONS = xbmc.translatePath('special://home/addons')
        for item in os.listdir(ADDONS):
            addon_id = Get_Addon_ID(item)
            if addon_id != '' and addon_id != None:
                enable_list.append(addon_id)

# If a set of addon ids have been sent through we use that list to traverse through
    if len(addon_paths) > 0:
        enable_list = addon_paths

# If we have new add-ons found on the system which haven't yet been enabled
    if len(enable_list) > 0:
        for addon in enable_list:
            dolog('Checking dependencies for : %s'%addon)
            dependencies = Dependency_Check(addon_id=addon, recursive=True)

# traverse through the dependencies in reverse order attempting to enable
            for item in reversed(dependencies):
                if not item in exclude_list and not item in final_enabled and not item in skip:
                    dolog('Attempting to enable: %s'%item)
                    addon_set = Set_Setting(setting_type='addon_enable', setting=item, value = 'true')

# If we've successfully enabled then we add to list so we can skip any other instances
                    if addon_set or not os.path.exists(item):
                        final_enabled.append(item)

# Now the dependencies are enabled we need to enable the actual main add-on
            if not addon in skip:
                addon_set = Set_Setting(setting_type='addon_enable', setting=End_Path(addon), value = 'true')
            if addon_set and not addon in final_enabled:
                final_enabled.append(addon)

# Finally let's do a force refresh on the repo's
    xbmc.executebuiltin('UpdateAddonRepos')
