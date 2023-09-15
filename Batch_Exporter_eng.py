# -*- coding:utf-8 -*-
# Author: 张来吃
# Version: 1.0.1
# Contact: laciechang@163.com

# -----------------------------------------------------
# This script runs inside Resolve only, move me to:
# macOS: /Users/{USER}/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit
# Windows: C:\Users\{USER}\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit
# -----------------------------------------------------

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
        self.project_manager.LoadProject(name)
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

    def add_render_job(self, preset, path, name):
        current_project = self.project_manager.GetCurrentProject()
        current_project.LoadRenderPreset(preset)
        current_project.SetRenderSettings({"TargetDir": path}, {"CustomName": name})
        current_project.AddRenderJob()
    
    def get_render_preset(self) -> list:
        ls = self.project_manager.GetCurrentProject().GetRenderPresetList()
        ls.reverse()
        return ls

PROJECT = Project()
Current_folder_name = str(PROJECT.project_manager.GetCurrentFolder())

TimelineErrorMsg = "Failed to obtain the timeline, try to see if the timeline could be opened, or confirm whether the timeline has not been created in the project."
ProjectErrorMsg = "Failed to obtain the project, please confirm that there are saved projects in the current folder."
UnknowErrorMsg = "Unknown error"
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
        ui.LineEdit({"ID": MainFilter, "PlaceholderText": "filter"}),
        ui.CheckBox({"ID":InvertFilter, "Text": "Invert", "Weight": 0})
    ]),
])

naming_group = ui.VGroup({"Spacing": 5, },[
    ui.ComboBox({"ID": ExportTimelineType, }),
    ui.LineEdit({"ID": NamePrefix, "PlaceholderText": "Prefix"}),
    ui.LineEdit({"ID": NameSuffix, "PlaceholderText": "Suffix"}),
])

location_group = ui.HGroup({"Spacing": 5, "Weight": 3},[
    ui.Button({"ID": OutputPick, "Text": "Location", "Weight": 0}),
    ui.LineEdit({"ID": OutputPath, "PlaceholderText": "Target path"}),
])

project_level_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "Projects to export: ", "Alignment": {"AlignRight": True, "AlignVCenter": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": CurrentProject, "Checked": True, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": AllProject, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}), 
    ])
])

project_content_or_itself = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "Operation in project: ", "Alignment": {"AlignRight": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": ExportTimelineFiles,     "Checked": True,"Text": "Export timeline", "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": RenderTimeline, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": ExportProj, "AutoExclusive": True, "Checkable": True , "Events": {"Toggled": True}, "Visible": False}),
    ])
])

timeline_level_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Weight": 1},[
        ui.Label({"Text": "Timelines to export: ", "Alignment": {"AlignRight": True, "AlignVCenter": True}}),
        ui.VGap()
    ]),
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.CheckBox({"ID": AllTimeline, "Checked": True , "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ui.CheckBox({"ID": CurrentTimeline, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}, "Visible": False}),
    ])
])

render_options = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.Label({"Text": "Render preset: ", "Alignment": {"AlignRight": True}}),
    ui.ComboBox({"ID": RenderPreset, })
])

timeline_options = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.Label({"Text": "Export timeline as: ", "Alignment": {"AlignRight": True}}),
    naming_group,
])

window_01 = ui.VGroup([
    ui.Label({"Text": "<a href='https://github.com/laciechang/resolve-batch-exporter' style='color: #FA5B4A; text-decoration: none'>Batch Exporter</a>", "Alignment": {"AlignHCenter": True, "AlignVCenter": True}, "Weight": 0.1, "OpenExternalLinks" : True,}),
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
        ui.Button({"ID": "Run", "Text": "Export", "Weight": 0, "Enabled": False})
    ]),
    ui.Label({"StyleSheet": "max-height: 10px;"}),
])
        

dlg = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    100, 300, # position when starting
                                    500, 630 #width, height
                         ], 
                        "WindowFlags":{
                            "Window": True,
                        }
                        }, window_01)

itm = dlg.GetItems()

itm[CurrentProject].Text =      "Current project only"
itm[AllProject].Text =          "Projects in current \"{0}\" folder".format("Root" if len(Current_folder_name) == 0 else Current_folder_name )
itm[ExportTimelineFiles].Text = "Export timelines"
itm[RenderTimeline].Text =      "Render timelines"
itm[AllTimeline].Text =         "All timelines in project"
itm[CurrentTimeline].Text =     "Current timeline"
itm[ExportProj].Text =          "Export project file"

itm[CurrentProject].ToolTip =      "Exporting in current opened project."
itm[ExportTimelineFiles].ToolTip = "Same as menu option: File > Export > Timeline..."
itm[RenderTimeline].ToolTip =      "Same as Add to Render Queue in Deliver page"
itm[AllTimeline].ToolTip =         "All timelines in current project"
itm[CurrentTimeline].ToolTip =     "First/default auto-loaded timeline when you open a project"
itm[ExportProj].ToolTip =          "Export project as .drp file"

itm[AllProject].ToolTip =          """All projects in current folder of project manager
Note that in order to prevent duplicate names,
the timeline files exported at this point will be exported to a subfolder named after the project name"""

itm[RenderPreset].ToolTip =        """Please confirm in the custom preset that 
the target rendered path, file name, etc. 
will not cause file overwriting due to duplicate names"""

itm[ExportTimelineFilesGroup].CurrentIndex = 1
itm[ExportTimelineGroup].CurrentIndex = 0
itm[ExportTimelineType].AddItems(list(Timeline_Type.keys()))
itm[RenderPreset].AddItems(list(PROJECT.get_render_preset()))

def error_dialog(msg):
    msg_main = ui.VGroup({"Spacing": 10}, [
        ui.Label({"ID": "msginfo","Text": msg, "Alignment": {"AlignHCenter": True, "AlignVCenter": True}}),
        ui.HGroup([
            ui.HGap(),
            ui.Button({"Text": "OK", "ID":"closeit","Weight": 0}),
            ui.HGap(),
        ])
    ])

    msg_win = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "err_msg", 
                        "WindowFlags": {"SplashScreen" : True},
                        }, msg_main)
    msg_itm = msg_win.GetItems()
    width = 300 + len(msg)*5
    width = width if width > 200 else 200
    msg_itm["err_msg"].Resize([width, 80])
    def _close(ev):
        disp.ExitLoop()

    msg_win.On["err_msg"].Close = _close
    msg_win.On["closeit"].Clicked = _close
    msg_win.Show()
    disp.RunLoop()
    msg_win.Hide()

def success_dialog(folder):
    msg = "Export successful~"
    msg_main = ui.VGroup({"Spacing": 10}, [
        ui.Label({"Text": msg, "Alignment": {"AlignHCenter": True, "AlignVCenter": True}}),
        ui.HGroup([
            ui.HGap(),
            ui.Button({"Text": "Take a look", "ID":"closeit","Weight": 0}),
            ui.HGap(),
        ])
    ])

    msg_win = disp.AddWindow({ 
                        "WindowTitle": "Batch Exporter", 
                        "ID": "success_msg", 
                        "WindowFlags": {"SplashScreen" : True},
                        }, msg_main)
    msg_itm = msg_win.GetItems()
    width = 300 + len(msg)*5
    width = width if width > 200 else 200
    msg_itm["success_msg"].Resize([width, 80])
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

    msg_win.On["success_msg"].Close = _close
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
                        p.add_render_job(itm[RenderPreset].CurrentText, output_folder, timeline.GetName())
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
