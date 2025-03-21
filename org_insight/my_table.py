"""提供org table和dataframe之间的转换"""
import pandas as pd


class MyTable:
    """
    负责读取org table的数据
    转化成DataFrame后，支持各种常见的统计操作
    并能转换回org table
    """
    def __init__(self, table=None, csvFilePath=None, showRowNum=10, indexCol=None):
        """
        table是org src block的变量，代表org table, 实际上是一个list<list>结构
        self.cols2代表字段名称下面的第二行, 参考tableToDF注释org table的使用格式约定
        self.hLines代表横线的行号, 输出回org table的时候可以用它保持横线不消失
        或者
        从csv文件读取数据，转换成DataFrame
        indexCol默认为None
        """
        self.table = table
        self.csvFilePath = csvFilePath
        self.showRowNum = showRowNum
        if self.table is not None:
            self.df, self.cols2, self.hLines = self.__tableToDF(self.table)
        else:
            if self.csvFilePath is not None:
                self.df = pd.read_csv(csvFilePath, index_col=indexCol)
                self.cols2 = []
                innerCols2 = []
                for idx, e in enumerate(self.df.columns.values):
                    innerCols2.append("")
                self.cols2.append(innerCols2)
                self.hLines = [2]

    def replaceNone(self, t):
        """
        将二维list里面的None替换成[]
        """
        t2 = []
        hLines = []
        for idx, l in enumerate(t):
            if l is None:
                hLines.append(idx)
            else:
                l2 = []
                for e in l:
                    l2.append(e)
                t2.append(l2)
        return t2, hLines

    def __tableToDF(self, table):
        """
        org table必须按照如下格式准备:
        1. 字段名写在第一行
        2. 第二行要有，可以为空，也可以是描述
        3. 第三行是分割线
        4. 之后都是数据
        @return 返回df以及字段名第二行的数据columns2, 比如: [["", "", ""]]
        """
        table2, hLines = self.replaceNone(table)
        df = pd.DataFrame(columns=table[0], data=table2[2::])    # t由list<list>转换成了DataFrame对象
        cols2 = []
        cols2.append(table[1])
        return df, cols2, hLines

    def toOrgTable(self):
        """
        将df的数据转换成list, 用于生成org table
        float要控制小数精度
        nan要变成空字符串
        """
        df2 = self.df
        if self.showRowNum is not None:
            df2 = self.df.iloc[0:0 + self.showRowNum:]
        t1 = df2.values.tolist()
        t2 = []
        for line in t1:
            line2 = []
            for idx, e in enumerate(line):
                line2.append(convertToDisplay(e, df2.dtypes[idx]))
            t2.append(line2)
        result = [list(df2)] + self.cols2 + t2
        for e in self.hLines:
            result.insert(e, None)
        return result

    def sumColumns(self, rowStart, rowEnd):
        """
        将[rowStart, rowEnd)范围的所有的数值column求和
        @return 返回一个Series对象
        """
        df2 = self.df.iloc[rowStart:rowEnd:]
        sumResult = df2.sum(axis=0, skipna=True)
        return sumResult

    def sumColumn(self, rowStart, rowEnd, colName):
        """
        将[rowStart, rowEnd)范围的所有的数值column求和
        @return 返回数值
        """
        df2 = self.df.iloc[rowStart:rowEnd:]
        return sum(df2[colName])

    def avgColumn(self, rowStart, rowEnd, colName):
        """
        将[rowStart, rowEnd)范围的所有的数值column求和
        @return 返回一个Series对象
        """
        df2 = self.df.iloc[rowStart:rowEnd:]
        s = 0.0
        for v in df2[colName].values:
            s += v
        return s / len(df2[colName].values)

    def subtractColumns(self, rowStart, rowEnd, a, b, c):
        """
        a列的值减去b列的值，结果保存到c列
        """
        df1 = self.df.iloc[0:rowStart:]
        df2 = self.df.iloc[rowStart:rowEnd:]
        df3 = self.df.iloc[rowEnd::]
        df2[c] = df2[a] - df2[b]
        df1 = df1.append(df2)
        df1 = df1.append(df3)
        self.df = df1

    def divColumns(self, rowStart, rowEnd, a, b, c):
        """
        a列的值/ b列的值，结果保存到c列
        """
        df1 = self.df.iloc[0:rowStart:]
        df2 = self.df.iloc[rowStart:rowEnd:]
        df3 = self.df.iloc[rowEnd::]
        df2[c] = df2[a] * 1.0 / df2[b]
        df1 = df1.append(df2)
        df1 = df1.append(df3)
        self.df = df1

    def addColumns(self, rowStart, rowEnd, a, b, c):
        """
        a列的值减去b列的值，结果保存到c列
        """
        df1 = self.df.iloc[0:rowStart:]
        df2 = self.df.iloc[rowStart:rowEnd:]
        df3 = self.df.iloc[rowEnd::]
        df2[c] = df2[a] + df2[b]
        df1 = df1.append(df2)
        df1 = df1.append(df3)
        self.df = df1

    def formatFloatValue(self, value):
        """
        保留浮点数2位小数
        """
        if value is not None:
            if value == value:
                return "{:.2f}".format(value)
        return ""

    def toFloat(self, cols):
        """
        将cols包含的字段都改为float类型
        """
        for c in cols:
            self.df[c] = self.df[c].map(lambda e: self.convertToFloat(e))
            self.df[c].astype(float)

    def toInt(self, cols):
        """
        将cols包含的字段都改为float类型
        """
        for c in cols:
            self.df[c] = self.df[c].map(lambda e: self.convertToInt(e))
            self.df[c] = self.df[c].astype('Int64')

    def convertToInt(self, e):
        s = str(e)
        if s in ['', 'None']:
            return None
        else:
            return int(s)

    def convertToFloat(self, e):
        s = str(e)
        if s in ['', 'None']:
            return None
        else:
            return float(s)

    def calCompoundNum(self, rowStart, rowEnd, colName):
        """
        将colName对应列在[rowStart, endStart)之间的数据计算复利数值
        colName中的每一个值都是在[0, 100]之间的数值
        """
        s0 = 1.0
        s = 1.0
        df2 = self.df.iloc[rowStart:rowEnd:]
        for v in df2[colName].values:
            s = s * (1 + v * 0.01)
        return ((s - s0) / s0) * 100

    def dataRowNum(self):
        """
        返回表包含的数据的行数，不包含字段行和hLines
        """
        return len(self.df.values)


def convertToDisplay(e, dtype):
    if pd.isna(e):
        return ""
    if pd.api.types.is_float_dtype(dtype):
        return "{:.6f}".format(e)
    return e


def toOrgTable(df, showRowNum=10):
    """
    将df的数据转换成list, 用于生成org table
    float要控制小数精度
    nan要变成空字符串
    """
    df2 = df
    if showRowNum is not None:
        df2 = df.iloc[0:0 + showRowNum:]
    t1 = df2.values.tolist()
    t2 = []
    for line in t1:
        line2 = []
        for idx, e in enumerate(line):
            line2.append(convertToDisplay(e, df2.dtypes.iloc[idx]))
        t2.append(line2)
    cols2 = []
    innerCols2 = []
    for idx, e in enumerate(df2.columns.values):
        innerCols2.append("")
    cols2.append(innerCols2)
    result = [list(df2)] + cols2 + [None] + t2
    return result


def convertToInt(e):
    s = str(e)
    if s in ['', 'None']:
        return None
    else:
        return int(s)


def toInt(df, cols):
    """
    将cols包含的字段都改为float类型
    """
    for c in cols:
        df[c] = df[c].map(lambda e: convertToInt(e))
        df[c] = df[c].astype('Int64')


def sumColumn(df, rowStart, rowEnd, colName):
    """
    将[rowStart, rowEnd)范围的所有的数值column求和
    @return 返回数值
    """
    df2 = df.iloc[rowStart:rowEnd:]
    return sum(df2[colName])


def print_full(df):
    """
    将DataFrame完整显示出来
    """
    pd.set_option('display.max_rows', len(df))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(df)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')
