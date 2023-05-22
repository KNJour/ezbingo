app.route('/create_cards', methods=['POST'])
def create_cards():
    data = {
            "user_id" : session['user_id'],
            "playlist_id" : session['playlist_id']
        }
    query = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
    songs = connectToMySQL('ezbingo').query_db(query,data)
    playlist = []
    for song in songs:
        full_song = song['title']
        if song['artist']:
            full_song = f'{full_song} ({song["artist"]})'
            playlist.append(full_song)
    # Gather desired settings from form
    free_space = request.form.get('free_space')
    grid_size = int(request.form.get('grid_size'))
    num_cards = int(request.form.get('num_cards'))
    cards_per_page = int(request.form.get('cards_per_page'))



    # Generate randomized song lists for each bingo card
    all_playlists = []
    for i in range(num_cards):
        random.shuffle(playlist)
        print(playlist)
        if free_space:
            playlist.insert(int(len(playlist)/2), 'FREE SPACE')
        all_playlists.append(playlist)

    # Generate PDF file with bingo cards
    bingo_cards_pdf = canvas.Canvas("music_bingo_cards.pdf", pagesize=letter)
    card_width = 3.5*inch if grid_size == 3 else 4.5*inch if grid_size == 4 else 5.5*inch
    card_height = card_width
    margin_x = (8.5*inch - card_width*cards_per_page)/(cards_per_page+1)
    margin_y = (11*inch - card_height*(num_cards//cards_per_page))/2
    x, y = margin_x, 11*inch - margin_y - card_height

# create bingo card with randomized song list
    for i, song_list in enumerate(all_playlists):
        bingo_cards_pdf.setFont('Helvetica-Bold', 14)
        bingo_cards_pdf.drawString(x+0.5*inch, y-0.3*inch, 'B I N G O')
        bingo_cards_pdf.setFont('Helvetica', 12)
        for j, song in enumerate(song_list):
            row = j // grid_size
            col = j % grid_size
            bingo_cards_pdf.drawString(x+col*card_width/grid_size+0.1*inch, y-(row+1)*card_height/grid_size+0.4*inch, song)

        if (i+1) % cards_per_page == 0 or i == len(all_playlists)-1:
            bingo_cards_pdf.showPage()
            if i != len(all_playlists)-1:
                x, y = margin_x, 11*inch - margin_y - card_height
        else:
            x += margin_x + card_width

    bingo_cards_pdf.showPage()
    bingo_cards_pdf.save()
    # response = Response(pdf, content_type='application/pdf')
    # response.headers['Content-Disposition'] = 'attachment; filename=bingo_cards.pdf'
    return 'Bingo cards generated successfully!'


# TEST ROUTE


@app.route('/generate_bingo_cards', methods=['POST'])
def generate_bingo_cards():
    data = {
            "user_id" : session['user_id'],
            "playlist_id" : session['playlist_id']
        }
    query = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
    songs = connectToMySQL('ezbingo').query_db(query,data)
    playlist = []
    for song in songs:
        full_song = song['title']
        if song['artist']:
            full_song = f'{full_song} ({song["artist"]})'
        playlist.append(full_song)

    num_cards = 100
    print(playlist)
    pdf_file = generate_pdf(playlist, num_cards)
    response = Response(pdf_file, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=bingo_cards.pdf'
    return response

def generate_pdf(songs, num_cards):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    for i in range(num_cards):
        random_songs = random.sample(songs, 25)
        table_data = [random_songs[n:n + 5] for n in range(0, 25, 5)]
        table = Table(table_data)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        elements.append(table)
        elements.append(PageBreak())

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf