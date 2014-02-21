#!/usr/bin/python
import os,re,subprocess,webbrowser

from Tkinter import *
from tkMessageBox import *


class Application(Frame):

	settingsPath=os.path.expanduser('~/.wp-db-migration.ini');
	exportPath="./"
	recursion=0

	def __init__(self, master=None):
		
		master.resizable(0,0)
		master.title('Wordpress DB Migration')
		master.protocol("WM_DELETE_WINDOW", self._saveSettings)
		
		Frame.__init__(self, master,padx=10,pady=10)
		self.mysql=StringVar()
		self.localUrl=StringVar()
		self.liveUrl=StringVar()

		self._loadSettings()
		self.createWidgets()
		self._getDbDetails()


		w = master.winfo_screenwidth()
		h = master.winfo_screenheight()
		
		x = w/2 - 600/2
		y = h/2 - 150/2
		master.geometry("%dx%d+%d+%d" % (600,150,x, y))
		master.lift()

	def createWidgets(self):

		Label(self,text="Path to MySQL: ").grid(row=0,sticky=W)
		Label(self,text="Local URL: ").grid(row=1,sticky=W)
		Label(self,text="Live URL: ").grid(row=2,sticky=W)
		
		Entry(self,width=50,textvariable=self.mysql).grid(row=0,column=1,sticky=W)
		Entry(self,width=50,textvariable=self.localUrl).grid(row=1,column=1,sticky=W)
		Entry(self,width=50,textvariable=self.liveUrl).grid(row=2,column=1,sticky=W)

		frame=Frame(self,pady=10)
		frame.grid(columnspan=2)

		self.exportBtn = Button(frame, text='Export DB',command=self.exportDb)
		self.exportBtn.grid(row=0,column=0)

		self.importBtn= Button(frame, text='Import DB',command=self.importDb)
		self.importBtn.grid(row=0,column=1)

		self.importBtn= Button(frame, text='Help',command=self.help)
		self.importBtn.grid(row=0,column=2)

		self.pack()

	def _loadSettings(self):
		
		if os.path.isfile(self.settingsPath):
			f=open(self.settingsPath,'r')
			self.mysql.set(f.readline().strip())
			self.localUrl.set(f.readline().strip())
			self.liveUrl.set(f.readline().strip())
		else:
			self.mysql.set('/Applications/MAMP/Library/bin/')
			self.localUrl.set('http://localhost:8888/my_wp_db')
			self.liveUrl.set('http://mywp.wordpress.com/')

	def _saveSettings(self):
		f=open(self.settingsPath,'w')
		settings="\n".join([self.mysql.get().strip(),self.localUrl.get().strip(),self.liveUrl.get().strip()])
		f.write(settings)
		f.close()
		self.master.destroy()

	def _getIpAddress(self):
		proc = subprocess.Popen(["ifconfig -l"], stdout=subprocess.PIPE,shell=True)
		(out, err) = proc.communicate()
		for device in out.split(" "):
			proc = subprocess.Popen(["ifconfig "+device], stdout=subprocess.PIPE,shell=True)
			(_out, _err) = proc.communicate()
			# print(_out)
			if len(re.findall(r'status: active', _out))>0:
				result=re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',_out)
				return result[0]
		return None

	def _getDbDetails(self):
		path=self._findWPConfig(".")
		if path is not None:
			f=open(path,'r')
			config=f.read()
			f.close()

			# Find it based on the pattern, hopefully wordpress won't change it in the future
			# Added some \s* to allow some white spaces, in case someone accidentall added some space or tab
			result=re.findall(r'\'DB_NAME\'\s*,\s*\'[^\']*\'',config)
			# Found result will be like ['DB_NAME', 'my_wp_db']
			# Extract out my_wp_db 
			self.dbName=result[0].split("'")[-2]
			# Replace " with \", not likely in DB_NAME but password may contain quotes
			# Double quotes will break the generated shell command
			self.dbName=self.dbName.replace('"','\"')

			result=re.findall(r'\'DB_USER\'\s*,\s*\'[^\']*\'',config)
			self.dbUsername=result[0].split("'")[-2]
			self.dbUsername=self.dbUsername.replace('"','\"')

			dbPassword=re.findall(r'\'DB_PASSWORD\'\s*,\s*\'[^\']*\'',config)
			self.dbPassword=dbPassword[0].split("'")[-2]
			self.dbPassword=self.dbPassword.replace('"','\"')

	def _findWPConfig(self,path):
		self.recursion+=1
		if self.recursion > 10:
			showerror("Error!","Failed to find wp-config.php.\n\nPlease put this app inside your wordpress folder.")
			return None

		for dirname, dirnames,filenames in os.walk(path):
			for filename in filenames:
				if filename=="wp-config.php":
					return os.path.abspath(os.path.join(dirname,filename))
		return self._findWPConfig(os.path.abspath(os.path.join(path,os.pardir)))

	def exportDb(self):
		cmd="%s/mysqldump \"%s\" -u \"%s\" --password=\"%s\" > \"%s%s.sql\"" % (self.mysql.get(), self.dbName, self.dbUsername, self.dbPassword, self.exportPath, self.dbName)
		os.system(cmd)

		f=open(self.dbName+".sql",'r+')
		db=f.read()
		result=re.findall(r'\'siteurl\'\s*,\s*\'[^\']*\'',db)
		host=result[0].split("'")[-2]
		db=db.replace(host,self.liveUrl.get())
		
		f.seek(0)
		f.write(db)
		f.close()

	def importDb(self):
		pattern=re.compile('localhost',re.IGNORECASE)
		self.localUrl.set(pattern.sub(self._getIpAddress(),self.localUrl.get()))

		f=open(self.exportPath+self.dbName+".sql",'r')
		db=f.read()
		f.close()
		result=re.findall(r'\'siteurl\'\s*,\s*\'[^\']*\'',db)
		host=result[0].split("'")[-2]
		db=db.replace(host,self.localUrl.get())

		f=open("temp.sql",'w')
		f.write(db)
		f.close()

		cmd="%s/mysql -u \"%s\" --password=\"%s\" \"%s\" < temp.sql" % (self.mysql.get(), self.dbUsername, self.dbPassword, self.dbName)
		os.system(cmd)
		os.remove("temp.sql")
		pass
	def help(self):
		webbrowser.open('https://github.com/boratlibre/Wordpress-DB-Migration-Tool')

app = Application(Tk())

# The launched widnow doesn't focus.
# This is some hack to semi-solve the problem for now
if os.path.isfile('./__boot__.py'):
	app.exportPath='../../../'
	app.master.iconify()
	app.master.update()
	app.master.deiconify()
else:
	app.master.attributes('-topmost', 1)
	app.master.update()
	app.master.attributes('-topmost', 0)


app.master.mainloop()