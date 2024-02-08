from flask import Flask, app, render_template, request, redirect, url_for, session
import os
import random
import requests
from flask import url_for
import pandas as pd
from werkzeug.utils import secure_filename
from helper import EDA
from dotenv import load_dotenv
import subprocess
import time
load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = 'sony29tipo'  # Required for session management

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
images_dir = os.path.join(app.root_path, "static/retrived_data")
analysis_code_path = os.path.join(app.root_path, "analysis")
if not os.path.exists(analysis_code_path):
    os.makedirs(analysis_code_path)
if not os.path.exists(images_dir):
    os.makedirs(images_dir)


@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        description = request.form.get('description', '')  # Capture data description
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['filepath'] = filepath
            session['description'] = description  # Store description in session
            
            # Pass filename to redirect or render_template as needed
            return redirect(url_for("define_dataset", filename=filename))
    return render_template('upload.html')

@app.route('/define_dataset/<filename>')
def define_dataset(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath)
    session['columns'] = df.columns.tolist()
    return render_template('define_dataset.html', columns=session['columns'])
img = os.path.join('static', 'retrived_data')
def generate_image_path(image_file_name):
    """Generate the relative path for an image file to be used in the frontend."""
    image_rel_path = os.path.join(img, image_file_name)  # Use os.path.join for proper path handling
    print(image_rel_path, image_file_name)
    return image_rel_path

def generate_image(obj, prompt):
    tmp_filename = None
    try:
        response = obj.generate_response(prompt)
        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                    
        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
        image_rel_path = generate_image_path(image_file_name)   

        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
            return image_rel_path
        else:
            print(f"Image file does not exist at {image_rel_path}")
    except:
        print("An exception occurred") 
    finally:
        if tmp_filename and os.path.exists(tmp_filename):
            os.unlink(tmp_filename)

@app.route('/eda', methods=['GET', 'POST'])
def eda():
    columns = session.get('columns', [])
    df_html = ""
    analysis_result_html = ""
    image_rel_path = ""
    if 'filepath' in session:
        filepath = session['filepath']
        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
        df_html = df.head(5).to_html(classes='dataframe')

    if request.method == 'POST':
        filepath = session.get('filepath', None)
        description = session.get('description', '')  # Retrieve description from session
        if not filepath:
            return "No dataset loaded", 400
        
        # Reinitialize EDA object (consider refactoring this pattern for efficiency)
        dataset_name = os.path.basename(filepath)
        save_code_path = os.path.join(app.root_path, 'analysis', dataset_name.replace('.csv', '_analysis.py'))
        obj = EDA(dataset_name, filepath, save_code_path, description, images_dir)
        action = request.form.get('action')

        custom_text = request.form.get('input_text')
        choose_option = request.form.get('input_option')

        column_name1 = request.form.get('column_name1', '')
        column_name2 = request.form.get('column_name2', '')
        plot_type = request.form.get('plot_type', '')

        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
        df_html = df.head(5).to_html(classes='dataframe')
        tmp_filename = None
        if custom_text and choose_option:
            prompt = custom_text
            custom_csv_path = False
            if choose_option == "dataframe":
                custom_csv_path = True

            try:
                    response = obj.generate_response(prompt)
                    tmp_filename, image_file_name, csv_file_name = obj.extract_and_save(response, "new_header2", custom_csv_path)
                                
                    result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                    if custom_csv_path:
                        csv_rel_path = os.path.join(images_dir,csv_file_name)
                        res_df = pd.read_csv(csv_rel_path)
                        columns = res_df.columns.tolist()
                        res_df_html = res_df.to_html(classes='dataframe')
                        if os.path.exists(os.path.join(app.root_path, csv_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=res_df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    else:
                        image_rel_path = generate_image_path(image_file_name)   
                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
            except:
                    print("An exception occurred") 
            finally:
                   if tmp_filename and os.path.exists(tmp_filename):
                         os.unlink(tmp_filename)
        else:
            option = None
            if action == 'handle_missing_values':
                option = 0  
            elif action == 'missing_stat':
                option = 1
            # elif action == 'multivariate_analysis':
            #     option = 2
            elif action == 'statistical_summary':
                option = 3
            elif action == 'univariate_analysis':
                option = 4
            elif action == 'multivariate_analysis':
                option = 5
            elif action == 'plot_column':
                option = 6
            elif action == 'pair_scatter_plots':
                option = 7
            elif action == 'correlation_heatmap':
                option = 8
            elif action == 'pattern_trends':
                option = 9
            else:
                option = 10

            analysis_result = None  # This will store either a DataFrame or a signal for images
            image_file_name = None  # This will store image paths if images are generated
            Executed = False
            match option:
                case 0:
                    analysis_result = obj.handle_missing_values(df)
                    if isinstance(analysis_result, pd.DataFrame):
                        analysis_result_html = analysis_result.to_html(classes='dataframe')
                        # print(analysis_result_html)
                    else:
                        analysis_result_html = "Analysis did not return a DataFrame."

                    return render_template('eda.html', 
                                        columns=session.get('columns', []),
                                        df_html=df_html,
                                        analysis_result=analysis_result_html,
                                        image_path=image_rel_path)  # If you have an image to display

                case 1:
                    analysis_result =  obj.missing_stat(df)
                    if isinstance(analysis_result, pd.DataFrame):
                        analysis_result_html = analysis_result.to_html(classes='dataframe')
                        # print(analysis_result_html)
                    else:
                        analysis_result_html = "Analysis did not return a DataFrame."

                    return render_template('eda.html', 
                                        columns=session.get('columns', []),
                                        df_html=df_html,
                                        analysis_result=analysis_result_html,
                                        image_path=image_rel_path)  # If you have an image to display

                case 2:
                    prompt = "first lowercase the column name and then In the given dataset Conduct multivariate analysis exploring the relationship between different features"
                    image_rel_path = generate_image(obj=obj, prompt=prompt)
                    render_template('eda.html', image_path=image_rel_path)  
                case 3:
                    prompt = "Create a command to compute and display a statistical summary for each column in the dataset"
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, _, csv_file_name = obj.extract_and_save(response, "new_header2", custom_csv_path=True)
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        csv_rel_path = os.path.join(images_dir,csv_file_name)
                        print(csv_rel_path, csv_file_name)

                        res_df = pd.read_csv(csv_rel_path)
                        columns = res_df.columns.tolist()
                        res_df_html = res_df.to_html(classes='dataframe')

                        if os.path.exists(os.path.join(app.root_path, csv_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=res_df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)

                case 4:
                    prompt = "Code perform univariate analysis on the"+column_name1+"column of the dataset using"+plot_type
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   

                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)
                case 5:
                    # prompt = "Generate Python code to conduct multivariate analysis exploring the relationship between" + column_name1 + "and" + column_name2 + "using" + plot_type
                    prompt = "Generate Python code to conduct multivariate analysis exploring the relationship between " + column_name1 + " and " + column_name2 + " using " + plot_type
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   

                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except Exception as e:  # Catch the exception and store it in variable 'e'
                        print(f"An exception occurred: {e}")
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)

                case 6:
                    prompt = "Write a script to plot a" + plot_type + "for the" + column_name1 +"column in the dataset"
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   

                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)   
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)

                case 7:
                    prompt = "Provide Python code for generating pair scatter plots to explore relationships between pairs of variables"
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   
                        print(result, result.returncode)
                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  

                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)
                case 8:
                    prompt = "Generate a script to display the correlation matrix between numerical features as a heatmap of the dataset"
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   

                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template('eda.html', columns=columns, df_html=df_html, analysis_result=analysis_result_html, image_path=image_rel_path)  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)

                case 9:
                    prompt = "Show the process of using EDA to find patterns and trends regarding"+column_name1+" with" + column_name2+" class."
                    try:
                        response = obj.generate_response(prompt)
                        tmp_filename, image_file_name, _ = obj.extract_and_save(response, "new_header2")
                                    
                        result = subprocess.run(["python3", tmp_filename], capture_output=True, text=True, timeout=30)
                        image_rel_path = generate_image_path(image_file_name)   

                        if os.path.exists(os.path.join(app.root_path, image_rel_path)) and result.returncode == 0:
                            return render_template(
                                                    'eda.html',
                                                    columns=columns,
                                                    df_html=df_html,
                                                    analysis_result=analysis_result_html,
                                                    image_path=image_rel_path
                                                )  
                        else:
                            print(f"Image file does not exist at {image_rel_path}")
                    except:
                        print("An exception occurred") 
                    finally:
                        if tmp_filename and os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)

                case _:
                    return "Option not recognized. Please provide a valid option for data analysis."
            if analysis_result_html is None:
                    df_html = df.to_html(classes='dataframe')
    
    # df_html = pd.read_csv(session.get('filepath', '')).to_html(classes='dataframe')  # Load 'df' and convert to HTML

    return render_template(
        'eda.html',
        columns=columns,
        df_html=df_html,
        analysis_result=analysis_result_html,
        image_path=image_rel_path
    )       

if __name__ == '__main__':
    app.run(debug=True)     