import argparse
from dataclasses import dataclass
from requests_html import HTMLSession
import re


@dataclass
class SingleLessonData:
    lessonId: str
    lessonName: str
    classroom: str
    weeks: str
    teacher: str
    type: str
    credit: float
    stuListId: str


@dataclass
class LessonDayData:
    label: str
    singleData: list[SingleLessonData]


@dataclass
class LessonWeekData:
    label: str
    dayData: list[LessonDayData]


@dataclass
class StudentLessonData:
    stuId: str
    lessons: list


# 注:这个只适配了命令行的格式
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='请输入学号')
    parser.add_argument('-id', default='2021214229', help='根据学号查找课表')
    stuId = parser.parse_args().id
    # stuId = "2021214229"
    session = HTMLSession()
    r = session.get('http://jwzx.cqupt.edu.cn/kebiao/kb_stu.php?xh=' + stuId)
    # print(r.html.html)
    # 新建一个课程数据
    lessonData = StudentLessonData(stuId, list())
    # 列表名
    weeks = list(map(lambda x: x.text, r.html.find('div#stuPanel thead tr td')))[1:6]
    # 保留周数
    for i in weeks:
        lessonData.lessons.append(LessonWeekData(i, list()))
    # 问候语
    print("~~~")
    print("你好呀,亲爱的" + r.html.find('div#head div')[1].text[33:] + "同学")
    print()
    today = r.html.find('div#head div')[2]
    week = today.text[5]  # 这周的标识
    day = today.text[12]
    print(day)
    print(
        "----------------------------------------------------" + today.text + "----------------------------------------------------")
    # 所有课程
    tmp = r.html.find('#stuPanel table tr td')
    courses = r.html.find('#stuPanel table tr td')[8:72]
    i = 0  # 指针,指向星期
    j = -1  # 指针,指向时间
    for x in courses:
        # 添加时间
        if i % 8 == 0:
            j = j + 1
            for y in range(5):
                lessonData.lessons[y].dayData.append(
                    LessonDayData(x.text, list()))
            i = i + 1
            continue
        # 添加课程
        else:
            # 改时间有多个课
            if len(x.absolute_links) > 1:
                a = re.split("div", x.html)
                k = 0  # a的索引指针
                for y in a:
                    if k % 2 == 0:
                        k = k + 1
                        continue
                    else:
                        test = re.split("<br/>", y)
                        # 没有课
                        if len(test) < 2:
                            i = i + 1
                            continue
                        # 有课,正则过滤
                        lessonWeek = ""
                        for a in test:
                            a = a.replace("\n", "").replace("\t", "").replace("<font color=\"#FF0000\">", ""). \
                                replace("</font>", "").replace("<span style=\"color:#0000FF\">", ""). \
                                replace("</span>", "")
                            a = a[18:38]

                        lessonData.lessons[(i - 1) % 8].dayData[j].singleData.append(
                            SingleLessonData(test[0], test[1], test[2], test[0][18:], test[4], "", 0, ""))
                        k = k + 1
            else:
                test = re.split("<br/>", x.html)
                # 没有课
                if len(test) < 2:
                    i = i + 1
                    continue
                # 有课,正则过滤(目前没用)
                for a in test:
                    a = a.replace("\n", "").replace("\t", "").replace("<font color=\"#FF0000\">", ""). \
                        replace("</font>", "").replace("<span style=\"color:#0000FF\">", ""). \
                        replace("</span>", "")
                    re.sub("<(.*)>", a, "")
                lessonData.lessons[(i - 1) % 8].dayData[j].singleData.append(
                    SingleLessonData(test[0], test[1], test[2], test[0][25:], test[4], "", 0, ""))
            i = i + 1
    # 打印星期
    print(end="\t\t")
    for x in weeks:
        print(x + "\t\t\t", end="")
    # 打印换行
    print()

    tmpData = [["" for i in range(8)] for j in range(5)]
    weekIndex = 0  # 指针,指向星期
    timeIndex = 0  # 指针,指向时间
    for x in lessonData.lessons:
        for y in lessonData.lessons[weekIndex].dayData:
            for z in y.singleData:
                # 判断是否有课
                if z.lessonName != "":
                    if z.weeks[int(week) - 1] == "1":
                        tmpData[weekIndex][timeIndex] = z.lessonName[9:20]  # 过滤太长的课
            timeIndex = (timeIndex + 1) % 8
        weekIndex = (weekIndex + 1) % 8
    # 转置25 +
    lesson = list(map(list, zip(*tmpData)))
    times = ["1、2节", "3、4节", "中午间歇", "5、6节", "7、8节", "下午间歇", "9、10节", "11、12节"]
    for i in range(len(lesson)):
        # "11,12节"后使用\t
        if i == 7:
            print(times[i] + "\t", end="")
        # 其他时间使用\t\t
        else:
            print(times[i] + "\t\t", end="")
        for j in range(len(lesson[0])):
            # 为了让星期五的课后不使用\t(命令行美观)
            if j == 4:
                print(lesson[i][j], end="")
            else:
                if lesson[i][j] == "":
                    print("\t\t\t", end="")
                elif len(lesson[i][j]) <= 4:
                    print(lesson[i][j] + "\t\t", end="")
                elif len(lesson[i][j]) <= 8:
                    print(lesson[i][j] + "\t\t", end="")
                elif len(lesson[i][j]) <= 9:
                    print(lesson[i][j] + "\t", end="")
                elif len(lesson[i][j]) <= 11:
                    print(lesson[i][j] + "\t", end="")
                else:
                    print(lesson[i][j] + "", end="")
        # 换行
        print()
    print("\t\t" + "\t\t\t" * (int(day) - 1) + "↑↑↑↑↑")
    input("~~~感受3G的魅力吧~~~")
