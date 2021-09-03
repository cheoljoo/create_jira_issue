#!/usr/bin/env python3

import errno
import os
import glob
import sys
import csv
import datetime
import subprocess
from multiprocessing import Process, Queue

import shutil
import tarfile
import zipfile
import argparse

import settings

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/proc_kernel_log')
sys.path.insert(0, dir_path + '/proc_main_log')
sys.path.insert(0, dir_path + '/proc_tigris_log')
sys.path.insert(0, dir_path + '/proc_memory_log')

from proc_kernel_log import proc_kernel_log
from proc_main_log import proc_main_log
from proc_tigris_log import proc_tigris_log
from proc_memory_log import proc_memory_log

from common.handle_csv_data_file import get_diff_time_of_two_keyword
from common.handle_csv_data_file import get_float_value
from common.handle_csv_data_file import get_K_value
from common.handle_csv_data_file import get_float_value

from common.handle_csv_data_file import append_sys_analysis

from common.handle_csv_data_file import  sort_res_csv_data_by_type
from common.handle_csv_data_file import  make_csv_with_field_name
from common.handle_csv_data_file import  split_res_csv_data_by
from common.handle_csv_data_file import  merge_input_csv_file

def traceme(func):
    def newfunc(*args, **kwargs):
        if (settings.show_proc_info):
            print(func.__name__, "( )")
        ret = func(*args, **kwargs)
        return ret

    return newfunc


@traceme
def launch_ia(file_url):

    file_name = file_url[file_url.rfind('/') + 1:]

    d_str = 'Debug_logout\n\n file_url=[{}] file_name[{}]____\n'.format(
        file_url, file_name)
    d_str += 'script file path is = [{}]\n'.format(os.path.abspath(__file__))

    cur_work_dir = os.getcwd()
    cur_work_dir = cur_work_dir.rstrip('/')

    file_full_url = cur_work_dir + '/' + file_url

    d_str += 'current path of THIS_PROCESS is = [{}]\n'.format(file_full_url)
    d_str += '__work_dir  = [{}]\n'.format(settings.__dst_dir)

    d_str = dbg_log(d_str)

    mkdir_name = extract_file(file_full_url, file_name, settings.__dst_dir)

    if (mkdir_name):
        inter_out = mkdir_name + '/' + settings.__inter_out_dir_name
        os.mkdir(inter_out)
        out_dir = mkdir_name
        d_str += '--> NOW OUTPUT_DIR  = [{}]\n'.format(out_dir)
        launch_ia_dir(mkdir_name, out_dir)
    else:
        print("ERROR:  single log file (not zipped file ) ")
        return ''

    out_dir_url = out_dir[out_dir.find('/'):]

    out_file_url = out_dir_url + '/' + settings.__output_html_dir + '/' + settings.__output_file_name

    dbg_log("out_file_url= {}\n".format(out_file_url))
    dbg_log('______end_of_Debug_logout\n\n\n')
    return out_file_url


def service_init_before_launch_ia():

    settings.init() #care for calling from django webserver



@traceme
def launch_ia_dir(in_dir, out_dir):

    if (settings.show_proc_info):
        print(">>>> CURRENT WORK DIR =", os.getcwd());
    inter_out = out_dir + '/' + settings.__inter_out_dir_name

    if (settings.show_proc_info):
        print(">>>> CFG_DIR = ", settings.__cfg_dir)
    print(">>>> IN_CSV_DIR = ", settings.input_csv_dir)
    print(">>>> IN_DIR = ", in_dir)
    if (settings.show_proc_info):
        print(">>>> INTER_DIR = ", inter_out)
    print(">>>> OUT_DIR = ", out_dir)

    in_cfg_dir = copy_cfg_dir(settings.__cfg_dir, out_dir)

    in_dir = in_dir.rstrip('/')
    if (settings.show_proc_info):
        print("in_dir = ", in_dir)

    cfg_f = open(in_cfg_dir + '/' + settings.__proc_cfg_file, 'r')
    delim = ','  #csv file

    cfg_lines = cfg_f.readlines()
    cfg_f.close()

    result = Queue()
    processing = []

    will_report_error = ''
    report_to_save = None

    for index, line in enumerate(cfg_lines):
        #print(line, end = '')

        item = line.split(delim)

        if (index == 0):

            for idx_it, it in enumerate(item):
                for key in settings.proc_tbl_head:
                    if (key == it):
                        settings.proc_tbl_head[key] = idx_it
                        break

            if (settings.show_proc_info):
                print(settings.proc_tbl_head)
            continue

        #FILE_NAME,PROC_NAME,SHELL_NAME,PRE_LOG_TYPE,LOG_TYPE,PRE_CFG,PRE_IN,PRE_OUT,
        _file_name = item[settings.proc_tbl_head['FILE_NAME']]
        _proc_name = item[settings.proc_tbl_head['PROC_NAME']]
        _shell_name = item[settings.proc_tbl_head['SHELL_NAME']]
        _pre_log_type = item[settings.proc_tbl_head['PRE_LOG_TYPE']]
        _log_type = item[settings.proc_tbl_head['LOG_TYPE']]

        if (_log_type == 'PCAP' and settings.__proc_pcap == False):
            continue

        _pre_cfg = item[settings.proc_tbl_head['PRE_CFG']]
        _pre_in = item[settings.proc_tbl_head['PRE_IN']]
        _pre_out = item[settings.proc_tbl_head['PRE_OUT']]

        search_name = in_dir + "/*/" + _file_name

        files = []
        for _dir,_,_ in os.walk(in_dir):
                files.extend(glob.glob(os.path.join(_dir, _file_name))) 

        #files = glob2.glob(search_name)
        if (settings.show_proc_info):
            print("_____in_dir[", search_name, "]___ : ", files)

        if (len(files) > 0):
            if (settings.show_proc_major):
                print("Launch --> TYPE:", _log_type, "  PROC_NAME:", _proc_name)

            str_file_list = "\n".join(files)
            flist_name = in_cfg_dir + '/' + settings.__file_list_name + _log_type.lower() + '.txt'
            if (settings.show_proc_info):
                print(str_file_list, "\n   <--- file_list  name=", flist_name)

            f_flist = open(flist_name, 'w')

            f_flist.write(str_file_list)
            f_flist.write("\n")
            f_flist.close()

            proc_name_param = settings.__root_dir_from_curr + '/' + _proc_name
            log_type_param = _pre_log_type + _log_type
            cfg_param = _pre_cfg + in_cfg_dir
            in_param = _pre_in + in_dir
            out_param = _pre_out + inter_out


            if (_shell_name == "python3"):
            #if (_shell_name == "xxx"):  #___for Test____
                proc = Process(target=call_func_proc_each_log_type,
                        args=(index, _proc_name, log_type_param, cfg_param, in_param, out_param, result))

            else:
                proc = Process(target=call_sub_proc_each_log_type,
                        args=(index, _shell_name, proc_name_param, log_type_param, cfg_param, in_param, out_param, result))
              
            proc.start()

            if (settings.processing_parallel == True):
                processing.append(proc)

            
            if (len(processing) == 0):
                #Handling serial processing
                proc.join()
                result.put("end_process")

                err_str = None
                #check result
                if (settings.__report_type == 'text'):
                    err_str, will_report_error, report_to_save = \
                        handle_result_of_proc(True, result, will_report_error, report_to_save)

                if (err_str != None):
                    break

            if (settings.show_proc_info):
                dbg_log("_____ Execute PROC_NAME: {}\n".format(_proc_name))


    #parallel processing
    if (len(processing) > 0):
        for proc in processing:
            proc.join()
            if (settings.__report_type == 'text'):
                err_str, will_report_error, report_to_save = \
                    handle_result_of_proc(False, result, will_report_error, report_to_save)

            if (err_str != None):
                break



    if (settings.show_proc_info):
        dbg_log("_____END_Done_with______  Execute PROC_**\n")
   

    err_str = compare_measure_data(inter_out, out_dir, err_str)


    if (settings.__report_type == 'text'):
        if (will_report_error != ''):
            if (err_str):
                err_str += will_report_error
            else:
                err_str = will_report_error

        make_output_text(inter_out, out_dir, err_str)
        
        if (err_str):
            dbg_log("exit with error")
            sys.exit(1)
    else:
        make_output_html(inter_out, out_dir)




@traceme
def handle_result_of_proc(wait_end, result, will_report_error, report_to_save):

    err_str = "no Return"
    while True:
        res = result.get()
        res_head = res[:4]
        if (settings.show_proc_info):

            head_str = res[:res.find('\n') - 1]
            print('res_head=', res_head, 'str=', head_str,  '<< end')
             #print('res_head=', res_head, 'str=', head_str)

        #
        # program erro --> "crit" : critical error
        # 
        # STOP  --> "fail"
        # ERROR --> "err"
        # SAVE  --> "save"
        #
        if (res_head == "fail"  or res_head == "crit"):
            rpt_str = "____Start fail_msg(error:)=\n"
            rpt_str += res
            rpt_str += "\n____End\n"
            err_str = rpt_str

        elif (res_head[:3] == "err"):
            if (settings.show_proc_major):
                print("_______ERROR_____________________")
            rpt_str = "___Start error_msg(error:)=\n"
            rpt_str += res
            rpt_str += "\n____End\n"

            if (settings.show_proc_info):
                print("RPT_STR____________ ", rpt_str)

            will_report_error += rpt_str

        elif (res_head == "save"):
            report_to_save += res
            
        elif (res_head == "succ"):
            err_str = None

        elif (res == "end_process"):
            break

        else:
            print("Unknown :", res);
            print("  --> Exit");
            sys.exit(1)

        if (wait_end == False):
            break;


    if (settings.show_proc_info):
        if (err_str != None):
            print(err_str)

    return err_str, will_report_error, report_to_save





@traceme
def call_func_proc_each_log_type(index, proc_name, log_type_param, cfg_param, in_param, out_param, result):

    param_list = (log_type_param, cfg_param, in_param, out_param, result)
    proc_func_name = proc_name.split('/')[0]

    if (settings.show_proc_info):
        print("[", index, "] ", "PARAM_LIST =", param_list, "proc_func_name =", proc_func_name)

    if (proc_func_name == "proc_main_log"):
        proc_main_log(*param_list)

    elif (proc_func_name == "proc_kernel_log"):
        proc_kernel_log(*param_list)
    
    elif (proc_func_name == "proc_tigris_log"):
        proc_tigris_log(*param_list)

    elif (proc_func_name == "proc_memory_log"):
        proc_memory_log(*param_list)


    else:
        print("Unknown proc_name =", proc_name)
        sys.exit(1)

    result.put("success  of " + log_type_param + '\n')



@traceme
def call_sub_proc_each_log_type(index, shell_name, proc_name_param, log_type_param, cfg_param, in_param, out_param, result):

    cmd_line_list = [
        shell_name, proc_name_param, log_type_param, cfg_param,
        in_param, out_param
    ]
    print("[", index, "] ", "CMD_LINE_LIST=", cmd_line_list)

    #subprocess.call(cmd_line_list)
    #proc = subprocess.Popen(cmd_line_list)
    #proc = subprocess.Popen(cmd_line_list, stdout=subprocess.PIPE)
    #proc = subprocess.Popen(cmd_line_list, stderr=subprocess.PIPE)
    proc = subprocess.Popen(cmd_line_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #proc.wait()
    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        str_stderr = str(stderr.decode())
        print("stderr =", str_stderr)

        print("Return Error : sub -", proc_name_param)
        result.put("fail")
        fail_str = "str_err: returncode={} stderr={}".format( int(proc.returncode), str_stderr)
        print("fail_str=", fail_str)
        result.put(fail_str)
    else:
        print("success")
        result.put("success of " + log_type_param + '\n')



def copy_cfg_dir(in_dir, out_dir):

    cfg_dir = out_dir + '/' + settings.__cfg_dir_name

    if (not os.path.isdir(cfg_dir)):
        os.mkdir(cfg_dir)

    if (settings.show_proc_info):
        print("____COPY cfg SRC=", in_dir, "DEST=", cfg_dir)

    copyDirectory(src=in_dir, dest=cfg_dir)

    src_file_list = []
    if (settings.input_csv_dir):

        for file in glob.glob(settings.input_csv_dir + "/expected_log_*.csv"):
           shutil.copy(file, cfg_dir)
        
        src_file_list.append("expected_log_*.csv")

    src_file_list.append("key_words.csv")
    merge_input_csv_file(cfg_dir, src_file_list, 'key_words_fit.csv')


    src_file_list = []
    src_file_list.append('key_words_proc.csv')
    merge_input_csv_file(cfg_dir, src_file_list,'key_words_proc_fit.csv')

    return cfg_dir

def do_compare(val, ref_v, comp_type):

    if (comp_type == "greater"):
        if (val > ref_v):
            print("condition -greater is satisfied")
            return True

    elif (comp_type == "less"):
        if (val < ref_v):
            print("condition -less is satisfied")
            return True

    return False



def compare_measure_data(in_dir, out_dir, err_str):

    if (settings.show_proc_major):
        print("compare_measure_data()")

    # 1. get booting time
    limit_boot_sec = datetime.timedelta(seconds = 30)

    diff_t = get_diff_time_of_two_keyword(in_dir, settings.result_expected_csv_name,
            "TIGER_PLATFORM_BOOTING",
            "TIGER_PLATFORM_BOOT_COMPLETED");

    if (diff_t):
        sys_info = "Elasped Booting_Time = " + str(diff_t.total_seconds())
        if (settings.show_proc_info):
            print(sys_info)

        append_sys_analysis(out_dir, settings.result_sys_analysis_csv_name,  sys_info)


        if ( do_compare(diff_t,  limit_boot_sec, "greater")):
            if (err_str == None):
                err_str = ""

            err_str += ("booting time [" + str(diff_t.total_seconds()) + "] is over (limit " + str(limit_boot_sec) + ")\n")


    # 2. get CPU usage (load average) at booting time

    limit_load_avg = 9.0
   
    load_v = get_float_value(in_dir, settings.result_memory_log_name, settings.load_average_tag, True)

    sys_info = "Load average at booting = " + str(load_v)

    if ( do_compare(load_v,  limit_load_avg, "greater")):
        if (err_str == None):
            err_str = ""

        err_str += ("CPU Load average [" + str(load_v) + "] is over (limit " + str(limit_load_avg) + ")\n")

    append_sys_analysis(out_dir, settings.result_sys_analysis_csv_name,  sys_info)



    # 3. get Memory usage (total PSS, USS) at booting time

    #ex>  5608371K  5591152K  TOTAL

    limit_pss_mem_size = 6 * 1024 * 1024 # 6 Gbyte

    pss_size = get_K_value(in_dir, settings.result_memory_log_name, settings.total_memory_pss_tag, True)

    sys_info = "Total Memory usage PSS (Kbyte) at booting = " + str(pss_size)

    if ( do_compare(pss_size,  limit_pss_mem_size, "greater")):
        if (err_str == None):
            err_str = ""

        err_str += ("Memory [PSS= " + str(pss_size) + "] is over (limit " + str(limit_pss_mem_size) + "K)\n")

    append_sys_analysis(out_dir, settings.result_sys_analysis_csv_name,  sys_info)


    limit_uss_mem_size = 6 * 1024 * 1024 # 6 Gbyte
    uss_size = get_K_value(in_dir, settings.result_memory_log_name, settings.total_memory_uss_tag, True)

    sys_info = "Total Memory usage USS (Kbyte) at booting = " + str(uss_size)

    if ( do_compare(uss_size,  limit_uss_mem_size, "greater")):
        if (err_str == None):
            err_str = ""

        err_str += ("Memory [USS= " + str(uss_size) + "] is over (limit " + str(limit_uss_mem_size) + "K)\n")

    append_sys_analysis(out_dir, settings.result_sys_analysis_csv_name,  sys_info)


    return err_str




def make_output_text(in_dir, out_dir, err_str):

    dbg_log("make_output_text()  >>>> IN and OUT_DIR= {}\n".format(in_dir + ' and ' + out_dir))

    sort_res_csv_data_by_type(in_dir, settings.result_expected_csv_name, 'TIME')
    make_csv_with_field_name(in_dir, settings.result_expected_csv_name, out_dir, settings.res_expected_head)

    src_dir = out_dir
    split_res_csv_data_by('MODULE_NAME', src_dir, settings.result_expected_csv_name, out_dir)


    if (not os.path.isdir(out_dir)):
        os.mkdir(out_dir)


    result_f_name = out_dir + "/result.txt"
    result = open(result_f_name, 'w')

    if (err_str):
        out_msg = "NOT_OK\n\n"
        out_msg += "---------- error report ----------\n"
        out_msg += err_str
        out_msg += "\n"
    else:
        out_msg = "OK\n"


    ## START__>>   for result_sys_analysis.csv file

    out_msg += "\n"
    out_msg += ">>  result_sys_analysis.csv File Content : \n"
    out_msg += "\n"
    result_sys = out_dir + '/' + settings.result_sys_analysis_csv_name
    fin = open(result_sys, 'r', errors='replace')
    lines = fin.readlines()
    fin.close()

    for line in lines:
        out_msg += ('\t' +  line )
    ## <<__END   for result_sys_analysis.csv file


    result.write(out_msg)
    result.close()
    print("\n" + out_msg)

    if (settings.show_proc_info):
        print("_____end_of  make_output_text")



def make_output_html(in_dir, out_dir):

    out_html_dir = out_dir + '/' + settings.__output_html_dir

    dbg_log(">>>> IN_DIR = {}\n".format(in_dir))
    dbg_log(">>>> OUT_DIR = {}\n".format(out_dir))
    dbg_log(">>>> OUT_HTML_DIR = {}\n".format(out_html_dir))

    _file = os.path.abspath(__file__)
    src_folder = _file[:_file.rfind('/') + 1]  +  "data/" + settings.__output_html_dir
    print("This file -- folder = ", src_folder)

    if (not os.path.isdir(out_html_dir)):
        os.mkdir(out_html_dir)

    print("____COPY html SRC=", src_folder, "DEST=", out_html_dir)
    copyDirectory(src=src_folder, dest=out_html_dir)

    _shell_name = 'python3'
    _make_output_cmd_name = 'make_output_html/make_output_html.py'
    _exec = settings.__root_dir_from_curr + '/' + _make_output_cmd_name
    cmd_line_list = ['python3', _exec, in_dir, out_html_dir]
    print("CMD_LINE_LIST = ", cmd_line_list)
    subprocess.call(cmd_line_list)

    print("_____ Execute MAKE_OUTPUT_CMD:", _make_output_cmd_name)




def copyDirectory(src, dest):
    from distutils.dir_util import copy_tree
    copy_tree(src, dest)


def dbg_log(msg):
    if (settings.__out_log_name == None):
        print(msg, end='')
        return ''

    fout = open(settings.__out_log_name, 'a')
    fout.write(msg)
    print(msg, end='')
    fout.close()
    return ''


def check_ftype_and_get_title(fname):
    zipfile_type = ['.zip', '.tar.gz', '.tar.bz2', '.tgz', '.tbz', '.7z']

    for fst in zipfile_type:
        #		print("check: " + fname + "fst: " + fst)
        #		print("lenth is {} ?= {}  rfine={}".format(len(fname), len(fst), fname.rfind(fst)) )

        if (fname.rfind(fst) > 0
                and ((len(fname) - len(fst)) == fname.rfind(fst))):
            print("Matched -- check: " + fname + "  fst: " + fst)

            title_txt = fname[:fname.rfind(fst)]
            return title_txt

    return ''


def extract_file(full_path_name, fname, to_directory='.'):

    mkdir_name = None
    dir_name_tail = '.dir'

    d_str = ''
    title_dir = check_ftype_and_get_title(fname)
    if (title_dir == ''):
        dbg_log("Could not extract file !\n")
        mkdir_name = to_directory + '/' + fname + dir_name_tail
        dbg_log("mkdir_name [{}] of to_directory [{}]\n".format(mkdir_name, to_directory))

        if (os.path.exists(mkdir_name)):
            dbg_log("Remove all files and dir _name=[{}]\n".format(mkdir_name))
            shutil.rmtree(mkdir_name)

        os.mkdir(mkdir_name)
        shutil.copy(full_path_name, mkdir_name)
        return

    if full_path_name.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif full_path_name.endswith('.tar.gz') or full_path_name.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif full_path_name.endswith('.tar.bz2') or full_path_name.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    elif full_path_name.endswith('.7z'):
        opener, cmd, pre_parm, post_parm = 'system', '7z', 'x', '-o'
    else:
        dbg_log("Could not extract {}\n".format(full_path_name))
        return

    mkdir_name = to_directory + '/' + fname + dir_name_tail 
    dbg_log("Title=[{}] mkdir_name=[{}]\n".format(title_dir, mkdir_name))

    if (os.path.exists(mkdir_name)):
        dbg_log("Remove all files and dir _name=[{}]\n".format(mkdir_name))
        shutil.rmtree(mkdir_name)


    if (opener == 'system'):

        cmd_line_list = ['7z', pre_parm, full_path_name, post_parm + mkdir_name]

        print(cmd_line_list)
        dbg_log("Extract CMD=[{}]\n".format(mkdir_name))
        subprocess.call(cmd_line_list)

    else:
        if (not os.path.exists(mkdir_name)):
            dbg_log("Make dir _name=[{}]\n".format(mkdir_name))
            os.mkdir(mkdir_name)

        cwd = os.getcwd()
        os.chdir(mkdir_name)

        try:
            file = opener(full_path_name, mode)
            try:
                file.extractall()
            finally:
                file.close()
        finally:
            os.chdir(cwd)

    return mkdir_name


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='tiger_ia.py',
        description=
        'Launcher for Log Analyzer of Intelligence Artificial about Tiger Log files'
    )

    parser.add_argument(
        'csv',
        type=str,
        metavar="CSV_DIR",
        help='name of directory for expected text(*.csv) files(expected_log_**.csv)')


    parser.add_argument('-i',
                        '--input_dir',
                        metavar="IN_DIR",
                        type=str,
                        help='folder names (mulitple)')

    parser.add_argument(
        '-f',
        '--input_file',
        metavar="IN_FILE",
        type=str,
        help=
        'input parameter for log_file (plain text) or zip_file which includes multiple log files'
    )

    parser.add_argument(
        '-s',
        '--stat_dir',
        metavar="STAT_DIR",
        type=str,
        help='name of directory for statistic data')

    parser.add_argument(
        '-o',
        '--output_dir',
        metavar="OUT_DIR",
        type=str,
        help='name of output directory which will has result.html file')

    
    parser.add_argument(
        '-r',
        '--report_type',
        metavar="REPORT_TYPE",
        type=str,
        help="report type : 'text' (default) or 'html'")

    parser.add_argument(
        '-t',
        '--test_result',
        metavar="TEST_RESULT",
        type=str,
        help='test result code by test-agent')

    parser.add_argument('--pcap', action='store_true')


    args = parser.parse_args()

    if (args.input_file == None and args.input_dir == None):
        print(
            "ERROR:  input parameter (use '-f' or '-i'). Usage: {} -h".format(
                sys.argv[0]))
        sys.exit(1)

    if (args.input_file and args.input_dir):
        print("ERROR:  do not use '-f' and '-i'). Usage: {} -h".format(
            sys.argv[0]))
        sys.exit(1)

    _file = os.path.abspath(__file__)
    _src_dir = _file[:_file.rfind('/')]
    _work_dir = os.getcwd()

    if (args.report_type == 'html' and _src_dir != _work_dir):
        print("ERROR:  Execute this program({}) in {}".format(
            sys.argv[0], _src_dir))
        print("INFO:  You must be running {} in {}".format(
            sys.argv[0], _work_dir))
        sys.exit(1)

    if (args.report_type != 'html'):
        report_type = 'text'
        if (args.pcap):
            process_pcap = True
        else:
            process_pcap = False

    else:
        report_type = 'html'
        process_pcap = True


    print("get TEST_RESULT code from test-agent", args.test_result)

    r_dir = os.path.dirname(os.path.abspath(__file__))


    csv_dir = args.csv
    dst_dir = args.output_dir
    log_name = ''

    csv_dir = csv_dir.rstrip('/')
    dst_dir = dst_dir.rstrip('/')


    settings.set_env_settings(report_type, csv_dir, dst_dir, r_dir, log_name, process_pcap)



    if (args.input_file):
        in_file = args.input_file
        if (os.path.isfile(in_file)):

            print(
                "input_csv_dir[{}] dst_dir[{}] \n in_file name[{}]".format(
                    settings.input_csv_dir, settings.__dst_dir, in_file))

            launch_ia(in_file)

        else:
            print("ERROR: input right log_file_name(ziped)")
            sys.exit(1)

    else:

        in_dir = args.input_dir
        if (os.path.isdir(in_dir)):

            if (not os.path.isdir(settings.__dst_dir)):
                os.mkdir(settings.__dst_dir)

            inter_out = settings.__dst_dir + '/' + settings.__inter_out_dir_name

            if (settings.show_proc_info):
                print("INTER_OUT= ", inter_out)

            if (not os.path.isdir(inter_out)):
                os.mkdir(inter_out)

            launch_ia_dir(in_dir, settings.__dst_dir)

        else:
            print("ERROR: input right input(logs) directory name")
            sys.exit(1)
