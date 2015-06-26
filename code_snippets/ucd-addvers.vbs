' Deliver a new file or group of files to uDeploy
'
' Adds qualifying files found recursively from a specified base directory or
' a component/base directory text list file.
' If version file options are passed, unzips the file being processed and if
' found, uses the tagged version naming for the uD version being added
'
' ver 1.3, 2013-09-05
' Daniel J Thompson
' djthomps@us.ibm.com
'  - Added post-process directory tree reconstruction option
'  - Minor update to help text
'  - Fixed work-offset CreateFolder problem
'  - Fixed CR/LF in version name problem
'
' ver 1.2, 2013-09-03
' Daniel J Thompson
' djthomps@us.ibm.com
'  - Added generic process property ${p:QualExts} for qualifying file extensions, defaults if not defined
'  - Added weburl ${p:WebUrl} & authtoken ${p:AuthToken} properties, expects external auth if not created
'  - Added more robust dependent file checking
'  - Fixed so base-path directory scan checks in found file only, not its base path
'  - Updated for better use of uD properties
'  - Minor update to help text
'
' ver 1.1, 2013-08-30
' Daniel J Thompson
' djthomps@us.ibm.com
'  - Fixed file list regex problem
'  - Made qualifying extensions more modifiable
'  - Added fail/continue option
'  - Updated help text
'  - Updated manifested version naming
'  - Updated manifested version match(es) processing
'
' ver 1.0, 2013-08-29
' Daniel J Thompson
' djthomps@us.ibm.com
'
Option Explicit

'*** Start of important settings
' Qualifying file extensions to process, will use defaults if no process property
Const cFileExts = "${p:QualExts}"
Const cFileExts_def = ".war"

' udclient authentication parameters
Const cWebUrl = "${p:WebUrl}"
Const cAuthToken = "${p:AuthToken}"

' Groovy bin & unzip plugin paths; will use defaults if no process property
Const cGroovy = "${p:agent/GROOVY_HOME}"
Const cUnzip = "${p:agent/AGENT_HOME}"
Const cGroovy_def = "c:\urbancode\udeploy\agent01\opt\groovy-1.8.8"
Const cUnzip_def = "c:\urbancode\udeploy\agent01\var\plugins"

' Groovy & FileUtils uD plugin unzip script
Const cGroovyFile = "groovy.bat"
Const cUnzipFile = "unzip.groovy"
'*** End of important settings

Const vbHide = 0
Const ForAppending = 0
Const ForReading = 1
Const ForWriting = 2
Const dq = """"

Dim objArgs, prmCompName, prmCleanUp, prmBasePath, prmManFile, prmManRegex, prmWorkOffs, prmManFlag, prmKeepDirs, rval
Set objArgs = WScript.Arguments
WScript.Echo ""
If objArgs.Count < 2 Then
	WScript.Echo "Error: no component and/or do-cleanup specified"
	WScript.Echo ""
	WScript.Echo "Syntax"
	WScript.Echo "cscript [/nologo] ucd-addvers.vbs component do-cleanup [base-path [work-offset [manifest-file manifest-regex [manifest-flag [keep-dirs]]]]]"
	WScript.Echo ""
	WScript.Echo "component is the uD component name for new verions when base-path is a directory"
	WScript.Echo ""
	WScript.Echo "do-cleanup can be '1','y','yes','true' to remove source files else work files"
	WScript.Echo "  only; use 'none' to keep all, moving work files to c:\temp for debugging"
	WScript.Echo ""
	WScript.Echo "base-path is usually an absolute path but can be a directory offset from the"
	WScript.Echo "  current one; specify a directory to be the base to search for all qualifying"
	WScript.Echo "  files; specify a file to be a 2 column list, newline seperated, of components"
	WScript.Echo "  and base paths to search for a qualifying file; if found, all files from the"
	WScript.Echo "  base will be included in the version created"
	WScript.Echo ""
	WScript.Echo "work-offset is usually a directory offset from the uDeploy work directory but"
	WScript.Echo "  can be an absolute path; work on a qualifying file* is done here"
	WScript.Echo "  * script must copy the file itself to the agent work area directory where"
	WScript.Echo "  this script is running for the unzip groovy plugin to function"
	WScript.Echo ""
	WScript.Echo "manifest-file is a file, likely preceded with a directory offset, found in an"
	WScript.Echo "  unpacked qualifying file that is scanned for matches using manifest-regex"
	WScript.Echo "  eg. META-INF/MANIFEST.MF"
	WScript.Echo ""
	WScript.Echo "manifest-regex is a pattern to scan a manifest-file with for a tagged version"
	WScript.Echo "  name, case-insensitive; both must have a value or have no value; a version"
	WScript.Echo "  name pattern must be within paranthesis in the regex pattern and multiple"
	WScript.Echo "  possibilities can be specified with the pipe character (|) separator"
	WScript.Echo "  eg. Implementation-Version:\s*([0-9.-]+)"
	WScript.Echo ""
	WScript.Echo "manifest-flag is a fail/continue flag; if manifest-regex fails, script will"
	WScript.Echo "  abort by default; set to '1','y','yes','true' to skip & continue"
	WScript.Echo ""
	WScript.Echo "keep-dirs is the number of empty directory levels to re-create after removal of"
	WScript.Echo "  source files when base-path is a list file; 0 or greater, default 2"
	WScript.Echo ""
	WScript.Echo "Enter """" to use parameter default when entering additional options"
	WScript.Echo ""
	WScript.Echo "Version name with no manifest-file is the qualifying file name, no extension"
	WScript.Echo "Version name with manifest-file is the tagged name returned by manifest-regex"
	WScript.Echo "Don't forget to double-quote where needed"
	WScript.Echo ""
	WScript.Echo "Installation of udclient to uD agent is required for this script to run.  The"
	WScript.Echo "udclient executable must be in the shell environment path."
	WScript.Quit -1
End If
prmCompName = objArgs(0)
prmCleanUp = LCase(objArgs(1))
prmBasePath = ""
prmWorkOffs = ""
prmManFile = ""
prmManRegex = ""
prmManFlag = ""
prmKeepDirs = 2
If objArgs.Count > 2 Then prmBasePath = objArgs(2)
If objArgs.Count > 3 Then prmWorkOffs = objArgs(3)
If objArgs.Count > 4 Then prmManFile = objArgs(4)
If objArgs.Count > 5 Then prmManRegex = objArgs(5)
If objArgs.Count > 6 Then prmManFlag = LCase(objArgs(6))
If objArgs.Count > 7 Then prmKeepDirs = objArgs(7)

' Reset default if needed
If prmBasePath = "" Then prmBasePath = "."

if (prmManFile = "" And prmManRegex <> "") Or (prmManFile <> "" And prmManRegex = "") Then
	WScript.Echo "Error: both version file parameters must be defined"
	WScript.Quit -1
End If

Dim oFolder, oRet, aDirs
Dim sGroovy, sUnzip, oGroovy, oUnzip
Dim fso, wso, oRE, oMatch
Set fso = CreateObject("Scripting.FileSystemObject")
Set wso = CreateObject("WScript.Shell")
Set oRE = New RegExp
aDirs = Array()

oRE.Global = False
oRE.Pattern = "^\d+$"
Set oMatch = oRE.Execute(prmKeepDirs)
If oMatch.Count = 0 Then
	WScript.Echo "Invalid value for keep-dirs"
	WScript.Quit -1
End If
prmKeepDirs = CInt(prmKeepDirs)

' Set & check path for groovy
sGroovy = cGroovy
'WScript.Echo sGroovy
If InStr(sGroovy, "${p:") = 1 And InStr(sGroovy, "}") = Len(sGroovy) Then sGroovy = cGroovy_def
'WScript.Echo sGroovy
If Not fso.FolderExists(sGroovy) Then
	WScript.Echo "Groovy directory '" & sGroovy & "' not found. Check agent file paths."
	WScript.Quit -1
End If
Set oFolder = fso.GetFolder(sGroovy)
Set oRet = Nothing
doFindLatest oFolder, cGroovyFile
If oRet Is Nothing Then
	WScript.Echo "Groovy executable '" & cGroovyFile & "' not found. Check agent file paths."
	WScript.Quit -1
End If
Set oGroovy = oRet
sGroovy = oGroovy.Path

' Set & check path for unzip
sUnzip = cUnzip
'WScript.Echo sUnzip
If InStr(sUnzip, "${p:") = 1 And InStr(sUnzip, "}") = Len(sUnzip) Then sUnzip = cUnzip_def
'WScript.Echo sUnzip
If Not fso.FolderExists(sUnzip) Then
	WScript.Echo "Unzip directory '" & sUnzip & "' not found. Check agent file paths."
	WScript.Quit -1
End If
Set oFolder = fso.GetFolder(sUnzip)
Set oRet = Nothing
doFindLatest oFolder, cUnzipFile
If oRet Is Nothing Then
	WScript.Echo "FileUtils plugin "' & cUnzipFile & "' script not found. Running a uD process with a FileUtils step on this agent should fix this."
	WScript.Quit -1
End If
Set oUnzip = oRet
sUnzip = oUnzip.Path

Dim qFileExts
qFileExts = cFileExts
If InStr(qFileExts, "${p:") = 1 And InStr(qFileExts, "}") = Len(qFileExts) Then qFileExts = cFileExts_def

Dim sWebUrl, sAuthToken
sWebUrl = cWebUrl
sAuthToken = cAuthToken
If InStr(sWebUrl, "${p:") = 1 And InStr(sWebUrl, "}") = Len(sWebUrl) Then sWebUrl = ""
If InStr(sAuthToken, "${p:") = 1 And InStr(sAuthToken, "}") = Len(sAuthToken) Then sAuthToken = ""
If sWebUrl = "" Then WScript.Echo "No udclient web URL passed, assume locally defined"
If sAuthToken = "" Then WScript.Echo "No udclient authentication token passed, assume locally defined"

Dim sCurPath, sWrkPath, sBaseDir
sCurPath = fso.GetAbsolutePathName(prmBasePath)
sWrkPath = fso.GetAbsolutePathName(prmWorkOffs)
sBaseDir = ""
'WScript.Echo sCurPath
'WScript.Echo sWrkPath
For Each rval In Split(sWrkPath, "\")
	If sBaseDir <> "" Then sBaseDir = sBaseDir & "\"
	sBaseDir = sBaseDir & rval
'WScript.Echo sBaseDir
	If Not fso.FolderExists(sBaseDir) Then fso.CreateFolder(sBaseDir)
Next
sWrkPath = sWrkPath & "\"
sBaseDir = ""

If fso.FolderExists(sCurPath) Then

	' Recursive scan of base directory
	WScript.Echo "'" & sCurPath & "' is a folder"
	WScript.Echo ""

	' Process base directory
	Set oFolder = fso.GetFolder(sCurPath)
	rval = doFolder(oFolder)

ElseIf fso.FileExists(sCurPath) Then

	' File list of components and base directories
	WScript.Echo "'" & sCurPath & "' is a file"
	WScript.Echo ""

	' Process list file
	Dim oListFile, sLine, nLine, idx
	Set oListFile = fso.OpenTextFile(sCurPath, ForReading)
	nLine = 0
	rval = 0
	Do Until oListFile.AtEndOfStream Or rval <> 0
		sLine = oListFile.ReadLine()
		nLine = nLine + 1
		oRE.IgnoreCase = True
		oRE.Global = False
		oRE.Pattern = "^[ \t]*(" & dq & "[^" & dq & "]+" & dq & "|[^ \t]+)[ \t]+(" & dq & "[^" & dq & "]+" & dq & "|[^ \t]+)[^ \t]*$"
'WScript.Echo oRE.Pattern
		Set oMatch = oRE.Execute(sLine)
		If oMatch.Count = 1 Then
			If oMatch.Item(0).Submatches.Count = 2 Then

				' Found matching line, validate path
				prmCompName = Replace(oMatch.Item(0).Submatches(0), dq, "")
				sCurPath = Replace(oMatch.Item(0).Submatches(1), dq, "")
'WScript.Echo "'" & prmCompName & "'  '" & sCurPath & "'"
				If fso.FolderExists(sCurPath) Then

					ReDim aDirs(-1)
					sBaseDir = sCurPath
					Set oFolder = fso.GetFolder(sCurPath)
					rval = doFolder(oFolder)
'*** oVal file or base dir?
					If rval = 0 And (prmCleanUp = "1" Or prmCleanUp = "y" Or prmCleanUp = "yes" Or prmCleanUp = "true") Then
						oFolder.Delete True
						idx = LBound(aDirs)
						While idx <= UBound(aDirs)
							sLine = aDirs(idx)
							If Not fso.FolderExists(sLine) Then fso.CreateFolder(sLine)
							idx = idx + 1
						Wend
					End If
					If rval = 3 Then rval = 0
				Else
					WScript.Echo "Line " & nLine & ": folder '" & sCurPath & "' not found"
				End If
			Else
				WScript.Echo "Invalid # of matches at line " & nLine & ": '" & sCurPath & "'"
			End If
		Else
			WScript.Echo "No matches at line " & nLine & ": '" & sCurPath & "'"
		End If
	Loop

Else
	WScript.Echo "Folder or file '" & sCurPath & "' not found"
	rval = -1
End If

WScript.Quit rval

'----
Function doFolder(oFldr)

'WScript.Echo "|-- " & oFldr.Path & "--|"
'WScript.Echo "'" & oFldr.Name & "'  '" & oFldr.ParentFolder & "'  '" & oFldr.Path & "'"
'WScript.Echo oFldr.SubFolders.Count
'WScript.Echo oFldr.Files.Count
	Dim bSame
	Dim oVal, sCmd, sDir, sNam, sVer
	Dim cnt, i, o, s
	doFolder = 0

	s = oFldr.Path
	If UBound(aDirs) >= 0 Then
		' Do current slash-count minus base slash-count
		i = aDirs(0)
		i = Len(i) - Len(Replace(i, "\", ""))
		i = Len(s) - Len(Replace(s, "\", "")) - i
	End If
	' First level or within limit?
	If prmKeepDirs > 0 And (UBound(aDirs) < 0 Or i < prmKeepDirs) Then
		o = UBound(aDirs) + 1
		ReDim Preserve aDirs(o)
		aDirs(o) = s
	End If
'WScript.Echo  prmKeepDirs & " " & UBound(aDirs)
'WScript.Echo  Join(aDirs, " -- ")
'WScript.Echo  ""
	
	' Check if source dir is same as uD work dir
'WScript.Echo fso.GetAbsolutePathName(oFldr.Path)
'WScript.Echo fso.GetAbsolutePathName(".\")
	bSame = False
	If fso.GetAbsolutePathName(oFldr.Path) = fso.GetAbsolutePathName(".\") Then
		bSame = True
		WScript.Echo "ALERT: Source directory and uD work directory are the same"
	End If

	' Process each file in current directory
	For Each oVal In oFldr.Files
		' Remove dot-extension
		sNam = oVal.Name
		i = InStrRev(sNam, ".")
		If i > 0 Then s = LCase(Mid(sNam, i))
		If i > 0 Then sNam = Left(sNam, i - 1)
'WScript.Echo "sNam:'" & sNam & "' s:'" & s & "' '" & qFileExts & "' = " & InStr(qFileExts, s)
		if Len(sNam) = 0 Or InStr(qFileExts, s) = 0 Then
			' Log only if debugging
			If prmCleanUp = "none" Then WScript.Echo "Skipping invalid filename '" & oVal.Path & "'"
		Else
			' Set version name base
			sVer = sNam

			' Can't copy files to themselves
			If Not bSame Then
				' Copy file to uD work dir (copy needs end slash & same dir as script)
				If fso.FileExists(".\" & oVal.Name) Then _
					WScript.Echo "WARNING: Source file also found in uD work directory - overwriting"
				oVal.Copy ".\", True
			End If
			
			' Is there a version file to process?
			If prmManFile <> "" Then
				' Unzip uD work dir copy of qualified file to named subdir
				sDir = sWrkPath & sNam
				If Not fso.FolderExists(sDir) Then fso.CreateFolder(sDir)

				' Make unzip props file
				s = sDir & "\unzip.props"
				Set o = fso.CreateTextFile(s, True)
'WScript.Echo Replace(sDir, "\", "/")
				o.WriteLine("dir=" & Replace(sDir, "\", "/"))
				o.WriteLine("overwrite=true")
				o.WriteLine("zip=" & oVal.Name)
				o.Close

				sCmd = sGroovy & " " & oUnzip.Path & " " & s
'WScript.Echo sCmd
				WScript.Echo "Expanding " & oVal.Name & "..."
				i = wso.Run("%comspec% /c " & sCmd & " 1>" & sDir & "\out.txt 2>" & sDir & "\err.txt", vbHide, True)

				' Check for & process version manifest
				s = sDir & "\" & prmManFile
				sVer = ""
				If fso.FileExists(s) Then
'WScript.Echo "Found '" & prmManFile & "'"
					Set o = fso.OpenTextFile(s, ForReading)
					s = o.ReadAll
					o.Close
					oRE.IgnoreCase = True
					oRE.Global = True
					oRE.Pattern = prmManRegex
					Set oMatch = oRE.Execute(s)
					If oMatch.Count = 1 Then
						' Make sure there is only one valid submatch
						For Each i In oMatch.Item(0).Submatches
'WScript.Echo "i '" & i & "'"
							If i <> "" And sVer <> "" Then
								WScript.Echo "More than 1 match in " & oMatch.Item(0).Submatches.Count & " item submatches; adjust regex pattern and try again."
								WScript.Echo s
								WScript.Echo "Skipping " & oVal.Name
								doFolder = 3	'don't delete base-dir & continue
								Exit For
							ElseIf i <> "" Then
								'sVer = sVer & "-" & i.Name
								sVer = i
							End If
						Next
						If sVer = "" Then
							cnt = oMatch.Item(0).Submatches.Count
							i = cnt & " item submatches"
							If cnt = 0 Then
								i = i & ", requires at least 1;"
							Else
								i = "No valid matches found in " & i & ";"
							End If
							WScript.Echo i & " adjust regex pattern and try again."
							WScript.Echo s
							If cnt > 0 Or (prmManFlag = "1" Or prmManFlag = "y" Or prmManFlag = "yes" Or prmManFlag = "true") Then
								WScript.Echo "Skipping " & oVal.Name
								doFolder = 3	'don't delete base-dir & continue
							Else
								WScript.Echo "Aborting to prevent incorrect version naming."
								doFolder = 2
							End If
						End If
					Else
						WScript.Echo oMatch.Count & " item matches, requires 1 only; adjust regex pattern and try again."
						WScript.Echo s
						If prmManFlag = "1" Or prmManFlag = "y" Or prmManFlag = "yes" Or prmManFlag = "true" Then
							WScript.Echo "Skipping " & oVal.Name
							doFolder = 3	'don't delete base-dir & continue
						Else
							WScript.Echo "Aborting to prevent incorrect version naming."
							doFolder = 1
						End If
					End If
				Else
					WScript.Echo "Did not find '" & prmManFile & "' - skipping " & oVal.Name
				End If

				' Remove work subdir (cannot have the end slash)
				If fso.FolderExists(sDir) Then
					If prmCleanUp <> "none" Then
'WScript.Echo "Deleting '" & sDir & "'"
						fso.DeleteFolder sDir, True
					Else
						s = "c:\temp\" & sNam
						If fso.FolderExists(s) Then
							WScript.Echo "Deleting old '" & s & "'"
							fso.DeleteFolder s, True
						End If
						fso.MoveFolder sDir, "c:\temp\"
					End If
				End If
				If doFolder <> 0 Then
					If sBaseDir <> "" Then Exit Function	' Always if doing a list file
					If doFolder <> 3 Then Exit Function	' Only if not a skip if doing directory scan
					sVer = ""	' In case there was a multi submatch
				End If
			End If

			If sVer <> "" Then
				' Clean out any CR/LF chars
				sVer = Replace(sVer, Chr(13), "")
				sVer = Replace(sVer, Chr(10), "")
				' Create the new version to uDeploy
				sCmd = "udclient"
				If sWebUrl <> "" Then sCmd = sCmd & " -weburl " & sWebUrl
				If sAuthToken <> "" Then sCmd = sCmd & " -authtoken " & sAuthToken
				sCmd = sCmd & " createVersion -component """ & prmCompName & """ -name """ & sVer & Chr(34)
				WScript.Echo sCmd
				Set o = wso.Exec("%comspec% /c " & sCmd)
				s = ""
				Do
					i = o.Status
					s = s & o.StdOut.ReadAll
					s = s & o.StdErr.ReadAll
				Loop While i <> 0
				WScript.Echo s

'*** oVal file or base dir?
				s = LCase(s)	
				If InStr(s, "no component for") < 1 And InStr(s, "error processing command") < 1 Then
					If sBaseDir = "" Then
						s = oVal.ParentFolder.Path
						i = " -include """ & oVal.Name & dq
					Else
						s = sBaseDir
						i = ""
					End If
					sCmd = "udclient"
					If sWebUrl <> "" Then sCmd = sCmd & " -weburl " & sWebUrl
					If sAuthToken <> "" Then sCmd = sCmd & " -authtoken " & sAuthToken
					sCmd = sCmd & " addVersionFiles -component """ & prmCompName & """ -version """ & sVer & """ -base """ & s & dq & i
					WScript.Echo sCmd
					Set o = wso.Exec("%comspec% /c " & sCmd)
					s = ""
					Do
						i = o.Status
						s = s & o.StdOut.ReadAll
						s = s & o.StdErr.ReadAll
					Loop While i <> 0
					WScript.Echo s
				Else
					doFolder = 3	'don't delete base-dir & continue
				End If
' potential alternative
'i = wso.Run("C:\windows\system32\cmd.exe /c " & sCmd & " 1>\out-tmp.txt 2>\out-err.txt", vbHide, True)

'*** oVal file or base dir?
				' Remove source file itself (Boolean to force or not if r/o)
				If sBaseDir = "" Then
					if doFolder <> 3 Then
						If prmCleanUp = "1" Or prmCleanUp = "y" Or prmCleanUp = "yes" Or prmCleanUp = "true" Then oVal.Delete True
					Else
						doFolder = 0
					End If
				End If
			End If
			WScript.Echo ""
		End If
	Next

	If doFolder = 0 Then
		' Process each subdirectory
		For Each oVal In oFldr.SubFolders
'WScript.Echo "-->" & oVal.Name
			doFolder = doFolder(oVal)
			' Exit entire process if had an error
			If doFolder <> 0 Then Exit Function
		Next
	End If
End Function

'----
Sub doFindLatest(oFldr, sFile)

	Dim oVal

	' Process each file in current directory
	For Each oVal In oFldr.Files
		If LCase(oVal.Name) = LCase(sFile) Then
			If oRet Is Nothing Then Set oRet = oVal
			If oVal.DateLastModified > oRet.DateLastModified Then.Set oRet = oVal
		End If
	Next
	
	' Process each subdirectory
	For Each oVal In oFldr.SubFolders
'WScript.Echo "-->" & oVal.Name
		doFindLatest oVal, sFile
	Next

End Sub

'Sub doFindLatest(oFldr, sFile)
'
'	Dim oVal
'
'	' Process each file in current directory
'	For Each oVal In oFldr.Files
'		If LCase(oVal.Name) = LCase(sFile) Then
'			If oUnzip Is Nothing Then Set oUnzip = oVal
'			If oVal.DateLastModified > oUnzip.DateLastModified Then.Set oUnzip = oVal
'		End If
'	Next
'	
'	' Process each subdirectory
'	For Each oVal In oFldr.SubFolders
''WScript.Echo "-->" & oVal.Name
'		doFindLatest oVal, sFile
'	Next
'
'End Sub
