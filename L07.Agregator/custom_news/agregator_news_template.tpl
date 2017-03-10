<table border=1>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>#likes</th>
        <th>#comments</th>
    </tr>
    %for row in rows:
        %if row.class_label == 'good':
            <tr style = "background-color: green; color: white">
        %elif row.class_label == 'maybe':
            <tr style = "background-color: yellow">

        %else:
            <tr style = "background-color: red">
                %end
                <td><a href="{{row.url}}">{{row.title}}</a></td>
                <td>{{row.author}}</td>
                <td>{{row.points}}</td>
                <td>{{row.comments}}</td>
        </tr>
    %end
</table>

<a href="/update_news">I Wanna more HACKER NEWS!</a>.