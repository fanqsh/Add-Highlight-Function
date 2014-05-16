import sublime, sublime_plugin, os, shutil, re

def FomartMsg(szMsg):
    if not szMsg:
        szMsg = "";

    tbFomart = (".", "*", "(", ")", "[", "]", "^", "$", "?", "+", "|");
    szMsg = szMsg.replace("\\", "\\\\");
    for x in tbFomart:
        szMsg = szMsg.replace(x, '\\' + x);

    return szMsg;

def AddFunctionDic(szMsg, szMsgToAdd):
    if not szMsgToAdd or not szMsg:
        return;

    tbAddInfo = re.findall(re.compile("(\w+)\.(\w+)"), szMsgToAdd);
    szType = ".";
    if not tbAddInfo or not tbAddInfo[0] or not tbAddInfo[0][0] or not tbAddInfo[0][1]:
        tbAddInfo = re.findall(re.compile("(\w+):(\w+)"), szMsgToAdd);
        szType = ":";
        if not tbAddInfo or not tbAddInfo[0] or not tbAddInfo[0][0] or not tbAddInfo[0][1]:
            return;


    tbMsgInfo = re.findall(re.compile(FomartMsg(tbAddInfo[0][0]) + "\\\\\\" + szType + "(\([\|\w]*\))"), szMsg);
    if tbMsgInfo:
        if re.findall(re.compile("[\(\|)]" + FomartMsg(tbAddInfo[0][1]) + "[\(\|)]"), tbMsgInfo[0]):
            return;

        par = re.compile(FomartMsg(tbAddInfo[0][0]) + "\\\\\\" + szType + "\(");
        szMsg = par.sub(tbAddInfo[0][0] + "\\\\" + szType + "(" + tbAddInfo[0][1] + "|", szMsg);
        return szMsg;

    szMsg = szMsg + "|" + tbAddInfo[0][0] + "\\" + szType + "(" + tbAddInfo[0][1] + ")";
    return szMsg;

def AddInfo(szMsg):
    szInfoPath = sublime.packages_path() + "\\Lua";
    if not os.path.isdir(szInfoPath) and not os.path.isfile(szInfoPath) or not szMsg:
        return;

    szOldMsg = szMsg;
    szMsg = szMsg.replace(".", '_');
    szMsg = szMsg.replace(":", '_');

    if not re.findall(re.compile("^\w+$"), szMsg):
        print(szMsg);
        print("szMsg err");
        return;

    szInfoPath = szInfoPath + "\\" + szMsg + ".sublime-snippet";
    szFileInfo = """<snippet>
    <content><![CDATA[""" + szOldMsg + """${1:(${2:})}]]></content>
    <tabTrigger>""" + szMsg+ """</tabTrigger>
    <scope>source.lua</scope>
    <description>_</description>
</snippet>""";
    fp = open(szInfoPath, "w");
    fp.write(szFileInfo);
    fp.close();
    return;

class AddHighlightFunctionCommand(sublime_plugin.WindowCommand):
    def run(self):
        szFilePath = sublime.packages_path() + "\\Lua\\Lua.tmLanguage";

        if not os.path.isdir(szFilePath) and not os.path.isfile(szFilePath):
            return;
        
        if not self.window.active_view().sel() or not self.window.active_view().substr(self.window.active_view().sel()[0]):
            print("not sel")
            return;

        nFileSize = os.path.getsize(szFilePath)
        fp = open(szFilePath, "r+");
        szFileBuf = fp.read(nFileSize);
        fp.close()

        szGetDicPara = re.compile("""<key>match</key>[^<>]*<string>[^<>]*\\\\b\(([^<>]*)\)\\\\b[^<>]*</string>[^<>]*<key>name</key>[^<>]*<string>support.function.library.lua</string>""", re.DOTALL)
        tbInfo = re.findall(szGetDicPara, szFileBuf);
        if not tbInfo or not tbInfo[0]:
            print("not tbInfo or not tbInfo[0]");
            return;
        
        szDicMsg = tbInfo[0];
        szNewMsg = szDicMsg;
        for tbPos in self.window.active_view().sel():
            szTmpMsg = self.window.active_view().substr(tbPos);
            if szTmpMsg:
                AddInfo(szTmpMsg);
                szTmpMsg = AddFunctionDic(szNewMsg, szTmpMsg);
            if szTmpMsg:
                szNewMsg = szTmpMsg;

        szNewFile = szFileBuf.replace(szDicMsg, szNewMsg);

        shutil.copyfile(szFilePath, szFilePath + "_back");
        fp = open(szFilePath, "w");
        fp.write(szNewFile);
        fp.close();






