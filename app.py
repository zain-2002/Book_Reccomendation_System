from flask import Flask,render_template,request
import pandas
import numpy as np

popular_df = pandas.read_pickle(open('popularlistlatest.pkl','rb'))
pt = pandas.read_pickle(open('ptrlatest.pkl','rb'))
books = pandas.read_pickle(open('booksnewlatest.pkl','rb'))
similarity_scores = pandas.read_pickle(open('similarity_scoresnewlatest.pkl','rb'))
ratings= pandas.read_pickle(open('ratingnewlatest.pkl','rb'))
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route('/collaborativerecommend')
def recommend_ui():
    return render_template('recommend.html', error_message=None)

@app.route('/recommend_books',methods=['post'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]
        similar_items1 = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:26]

        data = []
        data1=[]
        for i in similar_items1:
            item1 = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            ratings_total = ratings.merge(temp_df,on='ISBN')
            num_rating_total = ratings_total.groupby('Book-Title').count()['Book-Rating'].reset_index()
            num_rating_total.rename(columns={'Book-Rating':'num_ratings'},inplace=True)
            averag_rating_df = ratings_total.groupby('Book-Title')['Book-Rating'].mean().reset_index()
            averag_rating_df.rename(columns={'Book-Rating':'avg_ratings'},inplace=True)
            popularnew_df = num_rating_total.merge(averag_rating_df,on='Book-Title')
            popularnew_df =popularnew_df[popularnew_df['num_ratings']>=250].sort_values('avg_ratings',ascending=False).head(10)
            popularnew_df = popularnew_df.merge(books,on='Book-Title').drop_duplicates('Book-Title')[['Book-Title','Book-Author','Image-URL-M','num_ratings','avg_ratings']]
            if not popularnew_df.empty:
                item1.extend(list(popularnew_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item1.extend(list(popularnew_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item1.extend(list(popularnew_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data1.append(item1)

        for i in similar_items:
            item = []
            item1 = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

           
        return render_template('recommend.html', data=[data,data1], error_message=None)

    except Exception as e:
        print(f"An error occurred during recommendation: {str(e)}")
        # You can log the error or perform other error-handling actions here
        error_message = "An error occurred during recommendation."
        return render_template('recommend.html', error_message=error_message)
    


        print(f"An error occurred during recommendation: {str(e)}")
        # You can log the error or perform other error-handling actions here
        error_message = "An error occurred during recommendation."
        return render_template('recommend.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)