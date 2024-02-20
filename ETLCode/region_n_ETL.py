'''
DEPRECATED
Takes the GTD dataset and transforms it into a clean, performant
dataset tailored for terror group level analysis.
'''
import pandas as pd
import sys
import json
import os

#Going to use some relative paths, so need this as a safety.
script_directory = os.path.dirname(os.path.abspath(__file__))
print(script_directory)
os.chdir(script_directory)

def ReadRename(gtd_fpath,read_cols_fpath):
    """
    Reads in the gtd excel file, reads in the 
    needed columns, and performs some renaming.
    """
    rd_cols_df = pd.read_excel(read_cols_fpath)

    rd_rename_cols_dct = {}
    for ind,row in rd_cols_df.iterrows():
        orig_col = row['ReadCols'].strip()
        rename_col = row['RenameTo'].strip()
        rd_rename_cols_dct[orig_col] = rename_col
    
    print("reading into dataframe...this will take a while, excel is slow!")
    df = pd.read_excel(gtd_fpath, usecols = list(rd_rename_cols_dct.keys()))
    df.rename(columns=rd_rename_cols_dct,inplace=True)

    print("reading complete.")
    return df


def FilterToApplicableGroups_old(df,n_attacks_needed,exclude_groups_fpath):
    '''
    Filtered to named groups from the GTD who have committed more than
    n_attacks_needed. Exclude groups file gives the group names to ignore.
    '''
    print("identifying groups to keep")
    df_temp = df.copy()
    grps_df = df_temp[['Group1','Group2','Group3']]
    df_flat = grps_df.stack().reset_index(drop=True)
    group_counts_df = df_flat.value_counts().reset_index(name='Count')

    # only get groups with sufficent numbers of attacks
    group_counts_df = group_counts_df[group_counts_df['Count'] > n_attacks_needed]
    grps_to_keep_ls = group_counts_df['index'].tolist()

    # filter out the exclude groups
    excl_grps_df = pd.read_excel(exclude_groups_fpath, header=None)
    excl_grps_ls = excl_grps_df.iloc[:, 0].tolist()
    grps_to_keep_ls = [gname for gname in grps_to_keep_ls if gname not in excl_grps_ls]
    df_temp = df_temp[
    (df_temp['Group1'].isin(grps_to_keep_ls)) |
    (df_temp['Group2'].isin(grps_to_keep_ls)) |
    (df_temp['Group3'].isin(grps_to_keep_ls))]
    return df_temp

def BuildColumns(df):
    '''
    Builds a time and CityCountry feature. Also sets a verified bit per group involvement
    '''
    print("Creating some features")
    df_temp = df.copy()
    df_temp['EventDateTime'] = pd.to_datetime(df_temp[['Year', 'Month', 'Day']], 
                                        errors='coerce')
    
    df_temp['CityCountry'] = df['City'] + ', ' + df['Country']

    ##set verified
    df_temp['Group1Verified'] = None
    df_temp['Group2Verified'] = None
    df_temp['Group3Verified'] = None
    df_temp.loc[df_temp['Group1Uncertain']==0,'Group1Verified'] = 1
    df_temp.loc[df_temp['Group2Uncertain']==0,'Group2Verified'] = 1
    df_temp.loc[df_temp['Group3Uncertain']==0,'Group3Verified'] = 1
    df_temp.loc[df_temp['Group1Uncertain']==1,'Group1Verified'] = 0
    df_temp.loc[df_temp['Group2Uncertain']==1,'Group2Verified'] = 0
    df_temp.loc[df_temp['Group3Uncertain']==1,'Group3Verified'] = 0

    #drop columns we don't need
    df_temp = df_temp.drop(columns=['Month','Day','Group1Uncertain',
                                    'Group2Uncertain','Group3Uncertain'])
    return df_temp

def LongifyByGroup(df):
    '''
    Make our dataset long by group only. The other aspects can stay wide. Ugly,
    but works because this is beyond the capability of pd.melt() to my knowledge.
    '''
    grp1_cols = ['Group1','GroupSub1','Group1Claimed','Group1ClaimedMethod','Group1Verified']
    grp1_rename = {col: ''.join(filter(str.isalpha, col)) for col in grp1_cols}
    grp2_cols = ['Group2','GroupSub2','Group2Claimed','Group2ClaimedMethod','Group2Verified']
    grp2_rename = {col: ''.join(filter(str.isalpha, col)) for col in grp2_cols}
    grp3_cols = ['Group3','GroupSub3','Group3Claimed','Group3ClaimedMethod','Group3Verified']
    grp3_rename = {col: ''.join(filter(str.isalpha, col)) for col in grp3_cols}
    fill_cols = [col for col in df.columns if col not in grp1_cols+grp2_cols+grp3_cols]
    
    #Group1 temporary df
    grp1_df = df[grp1_cols+fill_cols].copy()
    grp1_df.rename(columns=grp1_rename,inplace=True)
    grp1_df = grp1_df[grp1_df['Group'].notna()]
    #Group2 temporary df
    grp2_df = df[grp2_cols+fill_cols].copy()
    grp2_df.rename(columns=grp2_rename,inplace=True)
    grp2_df = grp2_df[grp2_df['Group'].notna()]
    #Group3 temporary df
    grp3_df = df[grp3_cols+fill_cols].copy()
    grp3_df.rename(columns=grp3_rename,inplace=True)
    grp3_df = grp3_df[grp3_df['Group'].notna()]

    #Combine into a long dataset
    long_df = pd.concat([grp1_df, grp2_df, grp3_df], axis=0, ignore_index=True)
    return long_df

def SetDatatypesAndSort(df):
    '''
    Hard define what datatypes for each column. Cuts memory usage in half.
    Then, do some pre sorting that might help performance later. This will
    persist into the parquet file :)
    '''
    print("Setting datatypes and sorting")
    new_dtypes = {
        "Country": "category",
        "Region" : "category",
        "SubRegion": "category",
        "City" : "category",
        "Latitude": "float64",
        "Longitude" : "float64",
        "SpecificLocation" : "object",
        "AttackDetails" : "object",
        "AttackSuccess" : "int8",
        "SuicideAttack" : "int8",
        "AttackType1" : "category",
        "AttackType2" : "category",
        "AttackType3" : "category",
        "TargetType1" : "category",
        "TargetSubType1" : "category",
        "SpecificTarget1" : "category",
        "TargetNationality1": "category",
        "TargetType2" : "category",
        "TargetSubType2" : "category",
        "SpecificTarget2" : "category",
        "TargetNationality2": "category",
        "TargetType3" : "category",
        "TargetSubType3" : "category",
        "SpecificTarget3" : "category",
        "TargetNationality3": "category",
        "Group" : "category",
        "GroupSub" : "category",
        "GroupClaimedMethod" : "category",
        "MotiveDetails" : 'object',
        "WeaponType1" : "category",
        "WeaponSubType1" : "category",
        "WeaponType2" : "category",
        "WeaponSubType2" : "category",
        "WeaponType3" : "category",
        "WeaponSubType3" : "category",
        "PropertyDamaged" : "int8",
        "PropertyDamagedExtent" : "category",
        "PropertyDamageUSD" : "float64",
        "RansomUSD" : "float64",
        "RansomPaid" : "float64",
        "HostageOrKidnapOutcome" : "object",
        "EventDateTime" : "datetime64[ns]",
        "CityCountry" : "object"
    }
    ret = df.copy()
    ret = ret.astype(new_dtypes)
    ret = ret.sort_values(by=['Region','Group','EventDateTime'])
    return ret

def FilterToApplicableGroups(df,exclude_groups_fpath,n_groups_to_keep,year_thresh):
    '''
    Filtered to named groups from the GTD who have committed more than
    n_attacks_needed. Exclude groups file gives the group names to ignore.
    '''
    print("identifying groups to keep")
    df_temp = df.copy()
    #remove unaffiliated individuals / verified attacks only / after year threshold
    df_temp = df_temp[df_temp['IsUnaffiliatedIndividual'] != 1]
    df_temp = df_temp.drop(columns=['IsUnaffiliatedIndividual'])
    df_temp = df_temp[df_temp['GroupVerified'] == 1]
    if(year_thresh != None):
        df_temp = df_temp[df_temp['Year']>=year_thresh]

    # filter out the exclude groups
    excl_grps_df = pd.read_excel(exclude_groups_fpath, header=None)
    excl_grps_ls = excl_grps_df.iloc[:, 0].tolist()
    grps_to_keep_ls = [gname for gname in df_temp['Group'].tolist() if gname not in excl_grps_ls]
    df_temp = df_temp[df_temp['Group'].isin(grps_to_keep_ls)]

    # keep n top groups per region
    top_groups_per_region = df_temp.groupby(['Region', 'Group']).size().reset_index(name='Count')
    top_groups_per_region = top_groups_per_region.sort_values(by='Count', ascending=False).groupby('Region').head(n_groups_to_keep)
    df_merged = pd.merge(df_temp, top_groups_per_region, on=['Region', 'Group'], how='inner')

    return df_merged

if __name__ == "__main__":
    ## Extract
    gtd_fpath = r"../../data/globalterrorismdb_0522dist.xlsx"
    out_fpath_pqt =r"../../data/gtd_clean_dataset_pqt.parquet"
    out_fpath_csv =r"../../data/gtd_clean_dataset_csv.csv"
    read_cols_fpath = r"ReadCols.xlsx"
    exclude_groups_fpath = r"exclude_group_names.xlsx"
    df = ReadRename(gtd_fpath,read_cols_fpath)

    ## Transform
    year_thresh = None
    n_groups_to_keep = 5
    df = BuildColumns(df)
    df = LongifyByGroup(df)
    df = FilterToApplicableGroups(df,exclude_groups_fpath,n_groups_to_keep,year_thresh)
    df = SetDatatypesAndSort(df)
    

    ## Load
    print(df.info())
    df.to_parquet(out_fpath_pqt,index=False) #performant one
    df.to_csv(out_fpath_csv,index=False) #for visiblity

