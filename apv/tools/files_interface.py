import pandas as pd
import os as os

path_main = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    )


def Join_relPath_toHomePath_AndMakeDirsIfNotThere(
        rel_path: str,
        path_main=path_main):
    destiPath = os.path.join(path_main, rel_path)
    if not os.path.exists(destiPath):
        os.makedirs(destiPath)
        print('Created folder: ' + destiPath)
    return destiPath


def df_from_file(
        rel_path: str, path_main=path_main,
        skiprows=0, index_col=None,
        delimiter='\t|,|;',
        append_all_in_folder=False,
        names=None, header='infer'):
    '''
    rel_path: relative file path with file extension,
    in case of append_all_in_folder=True: rel_path = folder path
    and file extrionsion doesnt matter

    header=none if no header labels are there
    '''
    df = pd.DataFrame()

    def read_file(source_file):
        print('reading ' + source_file.split('\\')[-1])
        return pd.read_csv(
            source_file,
            skiprows=skiprows,
            delimiter=delimiter,
            index_col=index_col,
            names=names,
            header=header,
            engine='python')

    if append_all_in_folder:
        source_folder = os.path.join(path_main, rel_path)
        source_files = []
        for file_name in os.listdir(source_folder):
            source_files += [os.path.join(path_main, rel_path, file_name)]
        # generator (as list comprehension but without storing the actual
        # content, only what to loop, which is much faster)
        dfs = (
            read_file(source_file) for source_file in source_files
        )
        df = pd.concat(dfs)
    else:
        source_file = os.path.join(path_main, rel_path)
        try:
            df = read_file(source_file)
        except FileNotFoundError:
            folder_path = "/".join(source_file.split("\\")[:-1])
            if os.path.exists(folder_path):
                print("check filename: " + str(os.listdir(folder_path)))
    return df


def df_export(
        df, file_name, rel_path='',
        float_format='%1.3e', sep='\t',
        index=True, header=True):
    '''
    header: to rename columns provide a list of strings here
    float_formats = '%1.2e' for scientific, '%1.2f for float with
    2 after comma digits'
    '''
    desti_path = Join_relPath_toHomePath_AndMakeDirsIfNotThere(rel_path)
    file_path = os.path.join(desti_path, file_name + '.csv')
    df.to_csv(
        file_path, float_format=float_format,
        index=index, sep=sep, header=header)
    print('exported df to ' + desti_path)


def save_fig(
        fig, file_name, rel_path='', file_formats=['.jpg'],
        dpi=300, transparent=False):

    desti_path = Join_relPath_toHomePath_AndMakeDirsIfNotThere(rel_path)

    for file_format in file_formats:
        file_path = os.path.join(desti_path, file_name + file_format)
        fig.savefig(file_path, bbox_inches='tight',
                    dpi=dpi, transparent=transparent)
        print('saved fig ' + file_path)
