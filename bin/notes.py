#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import string
import os

APP_ROOT = os.path.dirname(__file__).replace('bin', '')
DATA_ROOT = os.path.join(APP_ROOT, 'data')
TABS_LETTERS = "#" + string.uppercase
W_HEIGHT = 675
W_WIDTH = 758
KINDLE_KB_DEST = "com.lvm.notes"


class Notes(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_border_width(0)
        self.window.set_title("L:A_N:application_ID:%s_PC:N_O:U" %
                                  KINDLE_KB_DEST)
        self.window.set_default_size(W_WIDTH, W_HEIGHT)
        self.window.set_size_request(W_WIDTH, W_HEIGHT)
        self.show_keyboard = False

        self.editores = {}

        self.notes()
        self.window.connect("destroy", self.close_app)
        self.window.show_all()

    def notes(self, *args, **kwargs):
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_BOTH)

        btn_save = gtk.ToolButton(gtk.STOCK_SAVE)
        sep = gtk.SeparatorToolItem()
        sep2 = gtk.SeparatorToolItem()
        sep3 = gtk.SeparatorToolItem()
        btn_close = gtk.ToolButton(gtk.STOCK_QUIT)
        btn_prev = gtk.ToolButton(gtk.STOCK_GO_BACK)
        btn_next = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        btn_next = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        btn_keyboard = gtk.ToolButton(gtk.STOCK_EDIT)

        toolbar.insert(btn_save, 0)
        toolbar.insert(sep, 1)
        toolbar.insert(btn_close, 2)
        toolbar.insert(sep2, 3)
        toolbar.insert(btn_prev, 4)
        toolbar.insert(btn_next, 5)
        toolbar.insert(sep3, 6)
        toolbar.insert(btn_keyboard, 7)

        btn_save.connect("clicked", self.save_page)
        btn_close.connect("clicked", self.close_app)

        btn_prev.connect("clicked", self.prev_page)
        btn_next.connect("clicked", self.next_page)

        btn_keyboard.connect("clicked", self.switch_keyboard)

        self.table = gtk.Table(2, 1, self.show_keyboard)
        self.minitable = gtk.Table(4, 1, self.show_keyboard)
        self.minitable.attach(toolbar, 0, 1, 0, 1)
        self.table.attach(self.minitable, 0, 1, 1, 2)

        self.window.add(self.table)

        self.notebook = gtk.Notebook()
        self.table.attach(self.notebook, 0, 1, 0, 1)

        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(True)
        self.notebook.set_show_tabs(True)
        self.notebook.set_tab_pos(gtk.POS_TOP)

        for letter in TABS_LETTERS:
            scrolledwindow = gtk.ScrolledWindow()
            scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
            scrolledwindow.set_size_request(W_WIDTH, W_HEIGHT)

            self.editores[letter] = gtk.TextView()
            scrolledwindow.add(self.editores[letter])
            self.load_page(letter)

            label = gtk.Label(" %s " % letter)
            self.notebook.append_page(scrolledwindow, label)

        self.window.connect("destroy", self.close_app)
        self.window.show_all()

    def switch_keyboard(self, *args, **kwargs):
        self.show_keyboard = False if self.show_keyboard else True
        self.table.set_homogeneous(self.show_keyboard)
        self.minitable.set_homogeneous(self.show_keyboard)
        if self.show_keyboard:
            os.system("lipc-set-prop -s com.lab126.keyboard open %s:abc:4" %
                      KINDLE_KB_DEST)
        else:
            os.system("lipc-set-prop -s com.lab126.keyboard close %s" %
                      KINDLE_KB_DEST)

    def prev_page(self, *args, **kwargs):
        self.notebook.prev_page()

    def next_page(self, *args, **kwargs):
        self.notebook.next_page()

    def load_page(self, letter, *args, **kwargs):
        if letter in self.editores.keys():
            letter_file = os.path.join(DATA_ROOT, 'data-%s.txt' % letter)
            textbuffer = self.editores[letter].get_buffer()
            try:
                if os.path.isfile(letter_file):
                    page = file(letter_file, 'r')
                    page_content = ''.join(page.readlines())
                    page.close()
                    textbuffer.set_text(page_content)
            except Exception as e:
                raise IOError(e.message + ' | %s seems missing :<' %
                              letter_file)

    def save_page(self, widget, *args, **kwargs):
        letter = TABS_LETTERS[self.notebook.get_current_page()]
        letter_file = os.path.join(DATA_ROOT, 'data-%s.txt' % letter)
        textbuffer = self.editores[letter].get_buffer()
        page_content = textbuffer.get_text(textbuffer.get_start_iter(),
                                           textbuffer.get_end_iter())
        try:
            page = file(letter_file, 'w')
            page.write(page_content)
            page.close()
        except Exception as e:
            raise IOError(e.message + ' | %s seems missing :<' %
                          letter_file)

    def close_app(self, *args, **kwargs):
        os.system("lipc-set-prop -s com.lab126.keyboard close %s" %
                  KINDLE_KB_DEST)
        gtk.main_quit()


def main():
    Notes()
    gtk.main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Exiting due to user interrupt."
        import sys
        sys.exit(1)
