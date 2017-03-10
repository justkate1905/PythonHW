<table border=1>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>#likes</th>
        <th>#comments</th>
        <th colspan="3">Label</th>
    </tr>
    %for row in rows:
        <tr>
            <td><a href="{{row.url}}">{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.points}}</td>
            <td>{{row.comments}}</td>
            <td><a href="/add_label?label=good&id={{row.id}}">Интересно</a></td>
            <td><a href="/add_label?label=maybe&id={{row.id}}">Возможно</a></td>
            <td><a href="/add_label?label=never&id={{row.id}}">Не интересно</a></td>
        </tr>
    %end
</table>
<a href="/update_news">I Wanna more HACKER NEWS!</a>.