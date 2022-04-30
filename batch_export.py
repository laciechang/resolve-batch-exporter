import os, subprocess, platform

resolve = bmd.scriptapp('Resolve')
fu = bmd.scriptapp('Fusion')
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

class Project():
    def __init__(self) -> None:
        self.project_manager = resolve.GetProjectManager()
        self.current_project = self.project_manager.GetCurrentProject()
        self.project_name = self.current_project.GetName()
        self.projects = self.project_manager.GetProjectListInCurrentFolder()

    def export_project(self, name, path, option=True):
        o = self.project_manager.ExportProject(name, path+str(name)+".drp", option)

    def current_timeline(self):
        return self.project_manager.GetCurrentProject().GetCurrentTimeline()

    def all_timelines_in_current_project(self):
        for i in range(1, self.project_manager.GetCurrentProject().GetTimelineCount()+1):
            yield self.project_manager.GetCurrentProject().GetTimelineByIndex(i)

    def export_timeline(self, name, path, types):
        if type(types) is list:
            self.current_timeline().Export(path + name, types[0], types[1])
        else:
            self.current_timeline().Export(path + name, types)

    def add_render_job(self, preset, path):
        current_project = self.project_manager.GetCurrentProject()
        current_project.LoadRenderPreset(preset)
        current_project.SetRenderSettings({"TargetDir": path})
        current_project.AddRenderJob()
    
    def get_render_preset(self) -> list:
        ls = self.project_manager.GetCurrentProject().GetRenderPresetList()
        ls.reverse()
        return ls

PROJECT = Project()
Current_folder_name = str(PROJECT.project_manager.GetCurrentFolder())

TimelineErrorMsg = "时间线获取失败,试试时间线能否打开,或者确认工程内是否还未新建时间线"
ProjectErrorMsg = "项目获取失败 请确认当前文件夹内有已保存的项目"
UnknowErrorMsg = "怪了 选项没勾上么"
CheckState = {"Checked": True, "Unchecked": False}
Timeline_Type = {
    "FCP7 XML":     {"suffix": ".xml","type": resolve.EXPORT_FCP_7_XML,},
    "EDL - CMX 3600":          {"suffix": ".edl","type": [resolve.EXPORT_EDL, resolve.EXPORT_NONE],},
    "FCPXML 1.3":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_3,},
    "FCPXML 1.4":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_4,},
    "FCPXML 1.5":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_5,},
    "FCPXML 1.6":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_6,},
    "FCPXML 1.7":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_7,},
    "FCPXML 1.8":   {"suffix": ".fcpxml","type": resolve.EXPORT_FCPXML_1_8,},
    "AAF":          {"suffix": ".aaf","type": [resolve.EXPORT_AAF, resolve.EXPORT_AAF_NEW],},
    "DaVinci Resolve Timeline": {"suffix": ".drt", "type": resolve.EXPORT_DRT,},
    "EDL - CDL":          {"suffix": ".edl","type": [resolve.EXPORT_EDL, resolve.EXPORT_CDL],},
    "EDL - SDL":          {"suffix": ".edl","type": [resolve.EXPORT_EDL, resolve.EXPORT_SDL],},
    "EDL - Missing Clips":          {"suffix": ".edl","type": [resolve.EXPORT_EDL, resolve.EXPORT_MISSING_CLIPS],},
    "HDR10 Profile A":          {"suffix": ".xml", "type": resolve.EXPORT_HDR_10_PROFILE_A,},
    "HDR10 Profile B":          {"suffix": ".xml", "type": resolve.EXPORT_HDR_10_PROFILE_B,},
    "Dolby Vision 2.9":         {"suffix": ".xml", "type": resolve.EXPORT_DOLBY_VISION_VER_2_9,},
    "Dolby Vision 4.0":         {"suffix": ".xml", "type": resolve.EXPORT_DOLBY_VISION_VER_4_0},
    "CSV":          {"suffix": ".csv","type": resolve.EXPORT_TEXT_CSV,},
    "Tabbed Text":  {"suffix": ".txt","type": resolve.EXPORT_TEXT_TAB,},
    }

SplitLine = {"StyleSheet": "max-height: 1px; background-color: rgb(10,10,10)",}

AllProject = 'AllProject'
CurrentProject = 'CurrentProject'
AllTimeline = 'AllTimeline'
CurrentTimeline = 'CurrentTimeline'
OutputPath = 'OutputPath'
RenderPreset = 'RenderPreset'
OutputPick = 'OutputPick'
NamePrefix = 'NamePrefix'
NameSuffix = 'NameSuffix'
ExportProj = 'ExportProj'
ExportTimelineFiles = 'ExportTimelineFiles'
ExportTimeline = 'ExportTimeline'
ExportTimelineType = 'ExportTimelineType'
RenderTimeline = 'RenderTimeline'
ProgressBarBG = 'ProgressBarBG'
ProgressBar = 'ProgressBar'
ExportTimelineFilesGroup = 'ExportTimelineFilesGroup'
MainFilter = 'MainFilter'
FilteredList = 'FilteredList'
InvertFilter = 'InvertFilter'
ExportTimelineGroup = 'ExportTimelineGroup'

filteredlist_group = ui.VGroup({"Spacing": 5},[
    ui.Tree({"ID": FilteredList, "AlternatingRowColors": True, "HeaderHidden": True,}),
    ui.HGroup({"Weight": 0, "Visible": False}, [
        ui.LineEdit({"ID": MainFilter, "PlaceholderText": "过滤一下"}),
        ui.CheckBox({"ID":InvertFilter, "Text": "反选", "Weight": 0})
    ]),
])

naming_group = ui.VGroup({"Spacing": 5, },[
    ui.ComboBox({"ID": ExportTimelineType, }),
    ui.LineEdit({"ID": NamePrefix, "PlaceholderText": "文件名前缀"}),
    ui.LineEdit({"ID": NameSuffix, "PlaceholderText": "文件名后缀"}),
])

location_group = ui.HGroup({"Spacing": 5, "Weight": 3},[
    ui.Button({"ID": OutputPick, "Text": "选取位置", "Weight": 0}),
    ui.LineEdit({"ID": OutputPath, "PlaceholderText": "导出路径"}),
])

project_level_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "要导出的项目范围", "Alignment": {"AlignRight": True, "AlignVCenter": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": CurrentProject, "Checked": True, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": AllProject, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}), 
    ])
])

project_content_or_itself = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "要导出的项目内容", "Alignment": {"AlignRight": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": ExportTimelineFiles,     "Checked": True,"Text": "导出时间线", "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": RenderTimeline, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": ExportProj, "AutoExclusive": True, "Checkable": True , "Events": {"Toggled": True}, "Visible": False}),
    ])
])

timeline_level_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "要导出的时间线", "Alignment": {"AlignRight": True, "AlignVCenter": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": AllTimeline, "Checked": True , "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": CurrentTimeline, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}, "Visible": False}),
    ])
])

render_options = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.Label({"Text": "使用渲染预设", "Alignment": {"AlignRight": True}}),
    ui.ComboBox({"ID": RenderPreset, })
])

timeline_options = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.Label({"Text": "将时间线导出为", "Alignment": {"AlignRight": True}}),
    naming_group,
])

window_01 = ui.VGroup([
    ui.Label({"Text": "<a href='https://github.com/laciechang/resolve-batch-exporter' style='color: #FA5B4A; text-decoration: none'>批量导出工具</a>", "Alignment": {"AlignHCenter": True, "AlignVCenter": True}, "Weight": 0.1, "OpenExternalLinks" : True,}),
    ui.HGroup({"Spacing": 1},
        [
            ui.VGroup({"Spacing": 15, "Weight": 3},[
                ui.Label(SplitLine),
                project_level_group,
                ui.Label({"StyleSheet": "max-height: 5px;"}),
                ui.Label(SplitLine),
                project_content_or_itself,
                ui.Label(SplitLine),
                ui.Stack({"ID": ExportTimelineFilesGroup, "Weight": 0},[
                    ui.VGroup({"Spacing": 5, "Weight": 0},[ui.VGap()]),
                    ui.VGroup({"Spacing": 5, "Weight": 0},[
                        timeline_level_group,
                        ui.Label({"StyleSheet": "max-height: 10px;"}),
                        ui.Stack({"ID": ExportTimelineGroup},[
                            ui.VGroup({"Spacing": 5, "Weight": 0},[
                                timeline_options,
                            ]),
                            ui.VGroup({"Spacing": 5, "Weight": 0},[
                                render_options
                            ]),
                        ]),
                    ]),
                ]),
                ui.Label({"StyleSheet": "max-height: 5px;"}),
                ui.Label(SplitLine),
            ]),
            ui.Label({"Weight": 0, "StyleSheet": "max-width: 30px;"}),
        ]
    ),
    ui.HGroup({"Weight": 0},[
        location_group,
        ui.Button({"ID": "Run", "Text": "导出", "Weight": 0, "Enabled": False})
    ]),
    ui.Label({"StyleSheet": "max-height: 10px;"}),
])
        

dlg = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    100, 300, # position when starting
                                    400, 630 #width, height
                         ], 
                        }, window_01)

itm = dlg.GetItems()

itm[CurrentProject].Text =      "仅此项目"
itm[AllProject].Text =          "当前{0}文件夹内的项目".format("根" if len(Current_folder_name) == 0 else Current_folder_name )
itm[ExportTimelineFiles].Text = "导出时间线"
itm[RenderTimeline].Text =      "渲染时间线"
itm[AllTimeline].Text =         "项目内所有时间线"
itm[CurrentTimeline].Text =     "当前时间线"
itm[ExportProj].Text =          "直接导出项目"

itm[CurrentProject].ToolTip =      "在当前打开的项目内进行导出"
itm[ExportTimelineFiles].ToolTip = "等同于菜单中 文件 > 导出 > 时间线"
itm[RenderTimeline].ToolTip =      "等同于交付页面中 添加渲染任务"
itm[AllTimeline].ToolTip =         "当前项目内所有的时间线"
itm[CurrentTimeline].ToolTip =     "等同于打开项目时默认开启的时间线"
itm[ExportProj].ToolTip =          "将项目导出为.drp文件"

itm[AllProject].ToolTip =          """即项目管理器中所处文件夹内的所有项目
注意 为了防止重名
此时导出的时间线文件将会导出到 按项目名称命名 的子文件夹"""

itm[RenderPreset].ToolTip =        """建议在自定义的预设中
确认渲染出的路径、文件名等
不会因为重名而导致文件覆盖"""

itm[ExportTimelineFilesGroup].CurrentIndex = 1
itm[ExportTimelineGroup].CurrentIndex = 0
itm[ExportTimelineType].AddItems(list(Timeline_Type.keys()))
itm[RenderPreset].AddItems(list(PROJECT.get_render_preset()))

def error_dialog(msg):
    msg_main = ui.VGroup({"Spacing": 10}, [
        ui.Label({"ID": "msginfo","Text": msg, "Alignment": {"AlignHCenter": True, "AlignVCenter": True}}),
        ui.HGroup([
            ui.HGap(),
            ui.Button({"Text": "好的", "ID":"closeit","Weight": 0}),
            ui.HGap(),
        ])
    ])

    msg_win = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "err_msg", 
                        "WindowFlags": {"SplashScreen" : True},
                        }, msg_main)
    msg_itm = msg_win.GetItems()
    msg_geo = msg_itm["msginfo"].GetGeometry()
    width = 300 + len(msg)*5
    width = width if width > 200 else 200
    msg_itm["err_msg"].Resize([msg_geo[2], 80])
    def _close(ev):
        disp.ExitLoop()

    msg_win.On["err_msg"].Close = _close
    msg_win.On["closeit"].Clicked = _close
    msg_win.Show()
    disp.RunLoop()
    msg_win.Hide()

def success_dialog(folder):
    msg = "导出完成"
    msg_main = ui.VGroup({"Spacing": 10}, [
        ui.Label({"Text": msg, "Alignment": {"AlignHCenter": True, "AlignVCenter": True}}),
        ui.HGroup([
            ui.HGap(),
            ui.Button({"Text": "打开看看", "ID":"closeit","Weight": 0}),
            ui.HGap(),
        ])
    ])

    msg_win = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "err_msg", 
                        "WindowFlags": {"SplashScreen" : True},
                        }, msg_main)
    msg_itm = msg_win.GetItems()
    width = 100 + len(msg)*5
    msg_itm["err_msg"].Resize([width if width > 200 else 200, 80])
    def _close(ev):
        disp.ExitLoop()

    def _close_and_open_folder(ev):
        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
        disp.ExitLoop()

    msg_win.On["err_msg"].Close = _close
    msg_win.On["closeit"].Clicked = _close_and_open_folder
    msg_win.Show()
    disp.RunLoop()
    msg_win.Hide()


def _ExportProj(ev):
    if checkstate(ExportProj):
        itm[ExportTimelineFilesGroup].CurrentIndex = 0
    else:
        itm[ExportTimelineFilesGroup].CurrentIndex = 1
        if checkstate(RenderTimeline):
            itm[ExportTimelineGroup].CurrentIndex = 1
        else:
            itm[ExportTimelineGroup].CurrentIndex = 0

def _show_project_list(ev):
    
    if checkstate(AllProject):
        itm[ExportProj].Visible = True
        itm[CurrentTimeline].Visible = True
    else:
        itm[ExportProj].Visible = False
        itm[CurrentTimeline].Visible = False
        itm[ExportTimelineFiles].Checked = True
        itm[AllTimeline].Checked = True

def _show_timeline_list(ev):
    itm[FilteredList].Clear()
    if checkstate(AllTimeline):
        timelines = list(PROJECT.all_timelines_in_current_project())
        toplevelitems = []
        for i in timelines:
            row = itm[FilteredList].NewItem()
            row.Text[0] = i.GetName()
            toplevelitems.append(row)
        itm[FilteredList].AddTopLevelItems(toplevelitems)

def _pickfile(ev):
    selected = fu.RequestDir()
    itm[OutputPath].Text = str(selected)
    return selected

def _fresh_run_button(ev):
    if len(itm[OutputPath].Text) > 0:
        itm["Run"].Enabled = True
    else:
        itm["Run"].Enabled = False

def _exit(ev):
    disp.ExitLoop()
dlg.On.MyWin.Close = _exit

def use_project_name_subfolder(folder):
    folder = folder + str(Project().project_name) + "/"
    os.mkdir(folder)
    return folder

def checkstate(name):
    return CheckState[itm[name].GetCheckState()]

def export_in_project(projectName):
    p = Project()
    output_folder = itm[OutputPath].Text
    if checkstate(ExportProj):
        p.export_project(projectName, output_folder)
    else:
        p.project_manager.LoadProject(projectName)
        #############################################
        if checkstate(RenderTimeline):
            # render
            if checkstate(AllTimeline):
                timelines = p.all_timelines_in_current_project()
                for timeline in timelines:
                    try:
                        p.current_project.SetCurrentTimeline(timeline)
                        p.add_render_job(itm[RenderPreset].CurrentText, output_folder)
                    except:
                        error_dialog(TimelineErrorMsg)
            elif checkstate(CurrentTimeline):
                p.add_render_job(itm[RenderPreset].CurrentText, output_folder)
            else:
                error_dialog(UnknowErrorMsg)
            #############################################
        elif checkstate(ExportTimelineFiles):
            if checkstate(AllProject):
                output_folder = use_project_name_subfolder(output_folder)
            timelines = p.all_timelines_in_current_project()
            type_name = itm[ExportTimelineType].CurrentText
            if checkstate(AllTimeline):
                for timeline in timelines:
                    try:
                        p.current_project.SetCurrentTimeline(timeline)
                        name = itm[NamePrefix].Text+timeline.GetName()+itm[NameSuffix].Text + Timeline_Type[type_name]["suffix"]
                        o = p.export_timeline(name, output_folder, Timeline_Type[type_name]["type"])
                    except:
                        error_dialog(TimelineErrorMsg)
            elif checkstate(CurrentTimeline):
                name = itm[NamePrefix].Text+p.current_timeline().GetName()+itm[NameSuffix].Text + Timeline_Type[type_name]["suffix"]
                o = p.export_timeline(name, output_folder, Timeline_Type[type_name]["type"])
            else:
                error_dialog(UnknowErrorMsg)
        else:
            error_dialog(UnknowErrorMsg)

def _run(ev):
    try:
        if checkstate(AllProject):
            projects = Project().project_manager.GetProjectListInCurrentFolder()
        elif checkstate(CurrentProject):
            projects = [Project().current_project]
        for projectName in projects:
            export_in_project(projectName)
        
        if not checkstate(RenderTimeline):
            success_dialog(itm[OutputPath].Text)
    except:
        error_dialog(ProjectErrorMsg)

dlg.On[AllProject].Toggled = _show_project_list
dlg.On[ExportProj].Toggled = _ExportProj
dlg.On[ExportTimelineFiles].Toggled = _ExportProj
dlg.On[OutputPick].Clicked = _pickfile
dlg.On[OutputPath].TextChanged = _fresh_run_button

dlg.On["Run"].Clicked = _run


dlg.Show()
disp.RunLoop()
dlg.Hide()
