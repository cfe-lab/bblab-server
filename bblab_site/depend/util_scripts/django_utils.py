# Checked for python 3.7

from django.http import HttpResponse
import os, datetime

# This function simulates the Apache directory indexes. Return this as
# an HttpResponse.
def dir_index_str(relative_path, request, parent_dir, script_path):
        real_path = os.path.dirname(os.path.realpath(script_path)) + "/" + relative_path

        table_contents = ('<tr><th valign="top"><img src="/icons/blank.gif"'
                          'alt="[ICO]"></th><th>Name</th><th>Last modified</th><th>Size</th>'
                          '<th>Description</th></tr><tr><th colspan="5"><hr></th></tr>'
                          '<tr><td valign="top"><img src="/icons/back.gif" alt="[PARENTDIR]">'
                          '</td><td><a href="{}">Parent Directory</a>       </td><td>&nbsp;</td>'
                          '<td align="right">  - </td><td>&nbsp;</td></tr>').format(parent_dir)
        
        item_count = 0  # This number is how many directories and files are displayed.
        with os.scandir(real_path) as dir_items:
                for entry in sorted(dir_items, key=lambda e: e.name):
                        if not entry.name.startswith('.'):
                                def choose_file(file_path):
                                        file_ex = os.path.splitext(file_path)[1]
                                        if file_ex == ".csv":
                                                return '<img src="/icons/image3.gif" alt="[CSV]">'
                                        elif file_ex == ".html":
                                                return '<img src="/icons/layout.gif" alt="[HTML]">'
                                        elif file_ex == ".txt":
                                                return '<img src="/icons/text.gif" alt="[TEXT]">'
                                        elif file_ex == ".plt":
                                                return '<img src="/icons/patch.gif" alt="[PLT]">'
                                        else:
                                                return '<img src="/icons/unknown.gif" alt="[FILE]">'

                                icon_picture = ('<img src="/icons/folder.gif" alt="[DIR]">' if not entry.is_file() else choose_file(entry.name))
                                icon = '<td valign="top">{}</td>'.format(icon_picture)
                                entry_name = entry.name + ("" if entry.is_file() else "/")
                                name = '<td><a href="{}">{}</a></td>'.format(entry_name, entry_name)
                                lm = '<td align="right">{}</td>'.format(datetime.datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M"))
                                size = '<td align="right">{}</td>'.format(str(int(round(int(entry.stat().st_size)/100))/10)+"K" if entry.is_file() else "-")
                                desc = '<td>&nbsp;</td>'
                                table_contents += "<tr>{}{}{}{}{}</tr>".format(icon, name, lm, size, desc)	
                                item_count += 1

        table_contents += '<tr><th colspan="5"><hr></th></tr>'

        table = "<table><tbody>{}</tbody></table>".format(table_contents)
        head = "<title>Index of {}</title>".format(request.get_full_path())
        body = '<div id="body-div"><h1>Index of {}</h1>{}<p>Item Count: {}</p></div>'.format(request.get_full_path(), table, item_count)

        return '{% extends "tool_base.html" %} {% block head %}'+head+'{% endblock %}{% block content %}'+body+'{% endblock %}'

# This function attempts to read a file and returns the HttpResponse with the file in it.
def read_file(filename, dir, script_path):
        # Only files that exists in the directory relative to this file's location can be read.
        # There is no way that users can append strings to go to a different location because
        # the file that is read is a choice from the list of existing files.
        # User input is the difference betweeen failing a file, and reading a file from a preset list.
        # Conclusion: THIS IS SECURE.

        output_dir_path = os.path.dirname(os.path.realpath(script_path)) + "/" + dir
        with os.scandir(output_dir_path) as dir_items:
                for entry in dir_items:
                        if entry.name == filename:
                                with open(output_dir_path + entry.name, 'r') as f:
                                        file_string = f.read()

                                if os.path.splitext(filename)[1] == ".html":
                                        return HttpResponse(file_string) # Displays html properly.
                                else:
                                        return HttpResponse('<pre style="word-wrap: break-word; white-space: pre-wrap;">{}</pre>'.format(file_string.replace("<", "&lt;").replace(">", "&gt;")))
        
        return HttpResponse("Invalid File")

