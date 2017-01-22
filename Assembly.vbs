Option Explicit


Dim oFso
Dim sFolderInput
Dim sFileOutput
Dim aArgs
Dim oObjects
Dim sDrops
Dim sDropCmd
Dim sCreates
Dim sCreateCmd
Dim sDBN
Dim sDBU
Dim sDBP


Set oFso = CreateObject("Scripting.FileSystemObject")

Call ProcessCmdLine()
Call CollectObjects()
Call BuildDependencies()
Call ProcessArgs()
Call WriteOutput()

'MsgBox "Complete"


Class ObjectInfo
	Public Name
	Public Drop
	Public Create
	Public Trigger
	Public Depends
	Public DependedBy
End Class


Sub ProcessCmdLine()

	aArgs = Array()

	Dim arg

	For Each arg In WScript.Arguments
		If LCase(Left(arg, 5)) = "/dbn=" Then
			sDBN = Mid(arg,6)
		ElseIf LCase(Left(arg, 5)) = "/dbu=" Then
			sDBU = Mid(arg,6)
		ElseIf LCase(Left(arg, 5)) = "/dbp=" Then
			sDBP = Mid(arg,6)
		ElseIf LCase(Left(arg, 2)) = "/i" Then
			sFolderInput = Mid(arg,3)
		ElseIf LCase(Left(arg, 2)) = "/o" Then
			sFileOutput = Mid(arg,3)
		Else
			ReDim Preserve aArgs(UBound(aArgs)+1)
			aArgs(UBound(aArgs)) = UCase(arg)
		End If
	Next

	sFolderInput = Trim(Replace(sFolderInput,  """", ""))
	sFileOutput  = Trim(Replace(sFileOutput, """", ""))

'	If sFolderInput = "" Then
'		sFolderInput = InputBox("Enter path to the folder with DDL files")
'	End If
'	
'	If sFileOutput = "" Then
'		sFileOutput = InputBox("Enter path to the output file")
'	End If
'
'	If UBound(aArgs) < LBound(aArgs) Then
'		Dim sText
'		sText = InputBox("Enter a list of database objects, separated by spaces")
'		aArgs = Split(UCase(Trim(sText)), " ")
'	End If
End Sub


Sub CollectObjects()

	Dim oFile
	Dim oStream
	Dim sName
	Dim oObject
	Dim nPos

	Set oObjects = CreateObject("Scripting.Dictionary")

	If Not oFso.FolderExists(sFolderInput) Then
		Exit Sub
	End If

	For Each oFile In oFso.GetFolder(sFolderInput).Files

		Set oObject = New ObjectInfo
	
		oObject.Name    = UCase(oFile.Name)
		oObject.Drop	= ""
		oObject.Create	= ""
		oObject.Trigger	= ""
		oObject.Depends = Array()
		oObject.DependedBy = Array()

		nPos = InStr(oObject.Name, ".")
		If 0 < nPos Then
			oObject.Name = Left(oObject.Name, nPos-1)
		End If

		Call ReadFileStream(oFso.OpenTextFile(oFile.Path), oObject)

		Call oObjects.Add(oObject.Name, oObject)
	Next
End Sub


Sub ReadFileStream(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 13)) = "-- BEGIN DROP" Then
			Call ReadSectionDrop(oStream, oObject)
		ElseIf UCase(Left(Trim(sLine), 14)) = "-- BEGIN TABLE" Then
			Call ReadSectionTable(oStream, oObject)
		ElseIf UCase(Left(Trim(sLine), 16)) = "-- BEGIN TRIGGER" Then
			Call ReadSectionTrigger(oStream, oObject)
		ElseIf UCase(Left(Trim(sLine), 17)) = "-- BEGIN FUNCTION" Then
			Call ReadSectionFunction(oStream, oObject)
		ElseIf UCase(Left(Trim(sLine), 13)) = "-- BEGIN VIEW" Then
			Call ReadSectionView(oStream, oObject)
			ElseIf UCase(Left(Trim(sLine), 13)) = "-- BEGIN PROC" Then
			Call ReadSectionProc(oStream, oObject)
		ElseIf UCase(Left(Trim(sLine), 16)) = "-- BEGIN DEPENDS" Then
			Call ReadSectionDepends(oStream, oObject)
		End If			
	Loop
End Sub


Sub ReadSectionDrop(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 11)) = "-- END DROP" Then
			Exit Sub
		End If

		oObject.Drop = oObject.Drop & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionTable(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 12)) = "-- END TABLE" Then
			Exit Sub
		End If

		oObject.Create = oObject.Create & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionTrigger(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 14)) = "-- END TRIGGER" Then
			Exit Sub
		End If

		oObject.Trigger = oObject.Trigger & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionFunction(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 15)) = "-- END FUNCTION" Then
			Exit Sub
		End If

		oObject.Create = oObject.Create & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionView(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 11)) = "-- END VIEW" Then
			Exit Sub
		End If

		oObject.Create = oObject.Create & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionProc(oStream, oObject)

	Dim sLine

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 11)) = "-- END PROC" Then
			Exit Sub
		End If

		oObject.Create = oObject.Create & sLine & vbCrLf
	Loop
End Sub


Sub ReadSectionDepends(oStream, oObject)

	Dim sLine
	Dim nPos
	Dim aDepends

	aDepends = Array()

	Do While Not oStream.AtEndOfStream
		sLine = oStream.ReadLine()

		If UCase(Left(Trim(sLine), 15)) = "-- END DEPENDS" Then
			Exit Do
		End If

		sLine = Trim(sLine)

		If Left(sLine, 2) = "--" Then
			sLine = UCase(Trim(Mid(sLine,3)))
			nPos = InStr(sLine, ".")
			If 0 < nPos Then
				sLine = Mid(sLine, nPos+1)
			End If
			If sLine <> "" Then
				ReDim Preserve aDepends(UBound(aDepends)+1)
				aDepends(UBound(aDepends)) = sLine
			End If
		End If
	Loop

	oObject.Depends = aDepends
End Sub


Sub BuildDependencies()
	
	Dim oItem
	Dim oObject
	Dim sDepend
	Dim aDependedBy

	For Each oItem In oObjects.Items

	 	If IsArray(oItem.Depends) Then
	 		For Each sDepend In oItem.Depends

	 			If oObjects.Exists(sDepend) Then

	 				Set oObject = oObjects(sDepend)
	 			
	 				aDependedBy = oObject.DependedBy
	 				
	 				If Not IsArray(aDependedBy) Then
	 					aDependedBy = Array()
	 				End If
	 				
	 				ReDim Preserve aDependedBy(UBound(aDependedBy)+1)
	 				Set aDependedBy(UBound(aDependedBy)) = oItem

	 				oObject.DependedBy = aDependedBy
	 			End If    
	 		Next
	 	End If
	Next
End Sub


Sub ProcessArgs()

	Dim sArg
	Dim sKey
	Dim sCmd
	Dim oObject

	sDrops = ""
	sDropCmd = ""
	sCreates = ""
	sCreateCmd = ""


	For Each sArg In aArgs
		sArg = UCase(Trim(sArg))

		sCmd = "M"

		If Len(sArg) > 2 Then
			If Mid(sArg, Len(sArg)-1,1) = ":" Then
				sCmd = Right(sArg,1)
				sArg = Mid(sArg, 1,Len(sArg)-2)
			End If
		End If
		
		If Right(sArg,1) = "*" Then
			sArg = Left(sArg, Len(sArg)-1)

			For Each sKey In oObjects.Keys
				If UCase(Left(sKey, Len(sArg))) = sArg Then					
					Call ProcessObject(oObjects(sKey), sCmd)
				End If
			Next
		ElseIf oObjects.Exists(sArg) Then
			Call ProcessObject(oObjects(sArg), sCmd)
		End If
	Next 
End Sub


Sub ProcessObject(oObject, sCmd)

	Dim aDependedBy
	Dim oItem
	Dim sKey


	Call ProcessDrops(oObject, sCmd)

	aDependedBy = oObject.DependedBy

	If IsArray(aDependedBy) Then
		For Each oItem In aDependedBy
			Call ProcessObject(oItem, sCmd)
		Next
	End If

	sKey = "-" & oObject.Name & "-"

	If InStr(sDrops, sKey) = 0 Then
		sDropCmd = sDropCmd & oObject.Drop
		sDrops = sDrops & sKey
	End If

	If InStr(sCreates, sKey) = 0 Then
		sCreateCmd = _
			"-- " & oObject.Name & vbCrLf & _
			oObject.Create & vbCrLf & vbCrLf & sCreateCmd

		If oObject.Trigger <> "" Then
			sCreateCmd = sCreateCmd & vbCrLf & vbCrLf
			sCreateCmd = sCreateCmd & "-- " & oObject.Name & " (TRIGGERS)" & vbCrLf
			sCreateCmd = sCreateCmd & oObject.Trigger
		End If

		sCreates = sCreates & sKey
	End If
End Sub


Sub WriteOutput()

	Dim oFile

	If sFileOutput = "" Then
		Exit Sub
	End If

	Set oFile = oFso.CreateTextFile(sFileOutput, True, False)
	Call oFile.Write(sDropCmd)
	Call oFile.WriteBlankLines(2)
	Call oFile.Write(sCreateCmd)
	Call oFile.Close()
End Sub


Sub ProcessDrops(oObject, sCmd)

	If sDBN = "" Then
		Exit Sub
	End If
	If oObject.Drop = "" Then
		Exit Sub
	End If
	If Not OpenDBConnection() Then
		Exit Sub
	End If

Stop
	Dim sDrops
	Dim sDrop
	Dim nLen
	Dim aTokens
	Dim bExist


	sDrops = UCase(oObject.Drop)
	sDrops = Replace(sDrops, vbCrLf, vbLf)
	sDrops = Replace(sDrops, vbCr, vbLf)
	sDrops = Replace(sDrops, vbTab, " ")

	Do
		nLen = Len(sDrops)
		sDrops = Replace(sDrops, "  ", " ")
	Loop Until nLen = Len(sDrops)

	oObject.Drop = ""

	For Each sDrop In Split(sDrops, vbLf)
		sDrop = Trim(sDrop)
		If sDrop <> "" Then
			If Right(sDrop,1) = ";" Then
				sDrop = Left(sDrop, Len(sDrop)-1)
			End If
			aTokens = Split(sDrop, " ")
			If sCmd = "A" Then
				bExist = False
			Else
				bExist = True
			End If
			If aTokens(0) = "DROP" Then
				Select Case aTokens(1)
					Case "TABLE"
						bExist = DoesExistTable(aTokens(2), "T")
					Case "TRIGGER"
						bExist = DoesExistTrigger(aTokens(2))
					Case "VIEW"
						bExist = DoesExistTable(aTokens(2), "V")
					Case "INDEX"	
						bExist = DoesExistIndex(aTokens(2))
					Case "PROCEDURE"
						bExist = DoesExistRoutine(Mid(sDrop, 16), "P")
					Case "FUNCTION"
						bExist = DoesExistRoutine(Mid(sDrop, 15), "F")
					Case "SPECIFIC"
						Select Case UCase(aTokens(2))
							Case "PROCEDURE"
								bExist = DoesExistSpecificRoutine(aTokens(3), "P")
							Case "FUNCTION"
								bExist = DoesExistSpecificRoutine(aTokens(3), "F")
						End Select
				End Select
			End If
			If bExist Then
				oObject.Drop = oObject.Drop & sDrop & ";" & vbCrLf
			End If
		End If
	Next
End Sub


Dim oConnection

Function OpenDBConnection()

	OpenDBConnection = True

	If IsObject(oConnection) Then
		If Not oConnection Is Nothing Then
			Exit Function
		End If
	End If

	OpenDBConnection = False

	Dim nError



	On Error Resume Next

		Set oConnection = CreateObject("ADODB.Connection")

		oConnection.ConnectionTimeout = 60
		oConnection.CursorLocation = 3		' adUseClient
		oConnection.Mode = 3				' adModeReadWrite

		Call oConnection.Open("Provider='IBMDADB2';Data Source='" & sDBN & "';", sDBU, sDBP)

	nError = Err.Number

	On Error Goto 0

	OpenDBConnection = (nError = 0)
End Function


Function DoesExistTable(ByVal sName, sType)

	Dim oCommand
	Dim oRecordset
	Dim sSchema
	Dim nPos


	nPos = InStr(sName, ".")
	If 0 < nPos Then
		sSchema = Left(sName, nPos-1)
		sName   = Mid(sName, nPos+1)
	End If
	

	Set oCommand = CreateObject("ADODB.Command")

	oCommand.ActiveConnection = oConnection
	oCommand.CommandTimeout = 60
	oCommand.CommandType = 1 ' adCmdText

	oCommand.CommandText = "select 1 from SYSCAT.TABLES where TABSCHEMA='" & sSchema & "' and TABNAME='" & sName & "' and TYPE='" & sType & "'"

	Set oRecordset = oCommand.Execute()

	DoesExistTable = Not (oRecordset.EOF And oRecordset.BOF)
End Function


Function DoesExistTrigger(ByVal sName)

	Dim oCommand
	Dim oRecordset
	Dim sSchema
	Dim nPos


	nPos = InStr(sName, ".")
	If 0 < nPos Then
		sSchema = Left(sName, nPos-1)
		sName   = Mid(sName, nPos+1)
	End If
	

	Set oCommand = CreateObject("ADODB.Command")

	oCommand.ActiveConnection = oConnection
	oCommand.CommandTimeout = 60
	oCommand.CommandType = 1 ' adCmdText

	oCommand.CommandText = "select 1 from SYSCAT.TRIGGERS where TRIGSCHEMA='" & sSchema & "' and TRIGNAME='" & sName & "'"

	Set oRecordset = oCommand.Execute()

	DoesExistTrigger = Not (oRecordset.EOF And oRecordset.BOF)
End Function


Function DoesExistIndex(ByVal sName)

	Dim oCommand
	Dim oRecordset
	Dim sSchema
	Dim nPos


	nPos = InStr(sName, ".")
	If 0 < nPos Then
		sSchema = Left(sName, nPos-1)
		sName   = Mid(sName, nPos+1)
	End If
	

	Set oCommand = CreateObject("ADODB.Command")

	oCommand.ActiveConnection = oConnection
	oCommand.CommandTimeout = 60
	oCommand.CommandType = 1 ' adCmdText

	oCommand.CommandText = "select 1 from SYSCAT.INDEXES where INDSCHEMA='" & sSchema & "' and INDNAME='" & sName & "'"

	Set oRecordset = oCommand.Execute()

	DoesExistIndex = Not (oRecordset.EOF And oRecordset.BOF)
End Function


Function DoesExistSpecificRoutine(ByVal sName, sType)

	Dim oCommand
	Dim oRecordset
	Dim sSchema
	Dim nPos


	nPos = InStr(sName, ".")
	If 0 < nPos Then
		sSchema = Left(sName, nPos-1)
		sName   = Mid(sName, nPos+1)
	End If
	

	Set oCommand = CreateObject("ADODB.Command")

	oCommand.ActiveConnection = oConnection
	oCommand.CommandTimeout = 60
	oCommand.CommandType = 1 ' adCmdText

	oCommand.CommandText = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='" & sSchema & "' and SPECIFICNAME='" & sName & "' and ROUTINETYPE='" & sType & "'"

	Set oRecordset = oCommand.Execute()

	DoesExistSpecificRoutine = Not (oRecordset.EOF And oRecordset.BOF)
End Function


Function DoesExistRoutine(ByVal sName, sType)

	Dim oCommand
	Dim oRecordset
	Dim sSchema
	Dim nPos
	Dim sParams
	Dim aTokens
	Dim sToken
	Dim sLength
	Dim sCommand


	nPos = InStr(sName, ".")
	If 0 < nPos Then
		sSchema = Left(sName, nPos-1)
		sName   = Mid(sName, nPos+1)
	End If

	nPos = InStr(sName, "(")
	If 0 < nPos And Right(sName,1) = ")" Then
		sParams = Mid(sName, nPos)
		sName   = Left(sName, nPos-1)
	End If

	
	If sParams = "" Then
		Set oCommand = CreateObject("ADODB.Command")

		oCommand.ActiveConnection = oConnection
		oCommand.CommandTimeout = 60
		oCommand.CommandType = 1 ' adCmdText

		oCommand.CommandText = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='" & sSchema & "' and ROUTINENAME='" & sName & "'"

		Set oRecordset = oCommand.Execute()

		DoesExistRoutine = Not (oRecordset.EOF And oRecordset.BOF)
		Exit Function
	End If


	sParams = Mid(sParams, 2, Len(sParams)-2)
	aTokens = Split(sParams, ",")
	sParams = ""

	For Each sToken In aTokens
		sToken = Replace(sToken, " ", "")	' LONG VARCHAR -> LONGVARCHAR   !!!
		nPos = InStr(sToken, "(")
		If 0 = nPos Then
			sLength = ""
		Else
			sLength = Mid(sToken, nPos)
			sToken  = Left(sToken, nPos-1)			
		End If
		Select Case sToken
			Case "CHAR"
				sToken = "CHARACTER"
			Case "INT"
				sToken = "INTEGER"
			Case "DEC"
				sToken = "DECIMAL"
			Case "NUM"
				sToken = "NUMERIC"
		End Select
		If sParams <> "" Then
			sParams = sParams & ","
		End If
		sParams = sParams & sToken & sLength
	Next


	sCommand = "select 1 from (select" & _
		" R.ROUTINESCHEMA, R.ROUTINENAME, R.SPECIFICNAME, R.ROUTINETYPE, " & _
		" coalesce(listagg(" & _
		"      replace(P.TYPENAME, ' ','') || case " & _
		"      when P.TYPENAME in ('CHARACTER','VARCHAR','LONG VARCHAR') then '(' || rtrim(char(P.LENGTH)) || ')'" & _
		"      when P.TYPENAME in ('DECIMAL') then '(' || rtrim(char(P.LENGTH)) || ',' || rtrim(char(P.SCALE)) || ')'" & _
		"      else '' end" & _
		"      , ',') within group (order by P.ORDINAL asc), '') as PARAMS " & _
		"from" & _
		"  SYSCAT.ROUTINES R" & _
		"    left outer join SYSCAT.ROUTINEPARMS P on P.ROUTINESCHEMA=R.ROUTINESCHEMA and P.SPECIFICNAME=R.SPECIFICNAME and P.ORDINAL > 0 " & _
		"where" & _
		" R.ROUTINESCHEMA='" & sSchema & "' " & _
		"group by R.ROUTINESCHEMA, R.ROUTINENAME, R.SPECIFICNAME, R.ROUTINETYPE) A " & _
		"where A.ROUTINENAME='" & sName & "' and A.PARAMS='" & sParams & "' and A.ROUTINETYPE='" & sType & "'"

	Set oCommand = CreateObject("ADODB.Command")

	oCommand.ActiveConnection = oConnection
	oCommand.CommandTimeout = 60
	oCommand.CommandType = 1 ' adCmdText

	oCommand.CommandText = sCommand

	Set oRecordset = oCommand.Execute()

	DoesExistRoutine = Not (oRecordset.EOF And oRecordset.BOF)
End Function

