# -*- coding: utf-8 -*-
#This file creates a chart of chords, chosen according to a pitch-dependent probability table, for a carillon with an arbitrary range.
#Next, it became primarily the code that avoids ledger lines via additional staves. 1/27/13
#Possible model: default behavior is piano staff; octave_treble = True, octave_bass = True, splits = 
#returns "piano_staff" containing n staffs.

#all three staffs present?
#saturated texture of the melody's intervals in three voices at different tempi.
#sometimes a whole phrase is marked more loudly than the rest of the soup, coming out and receeding back in.


from abjad import *
from random import randint, seed, choice
import os

#seed the random number generator
seed(1)

#layout and formatting - global 
    
def make_piano_staff():
    piano_staff = scoretools.PianoStaff()
    top_staff = Staff()
    top_staff.name = "top"
    bottom_staff = Staff()
    bottom_staff.name = "bottom"
    contexttools.ClefMark('bass')(bottom_staff)
    piano_staff.extend([top_staff, bottom_staff])
    #piano_staff.override.staff_grouper.staffgroup_staff_spacing.basic_distance = 200
    marktools.LilyPondCommandMark('override StaffGrouper.staffgroup-staff-spacing.basic-distance = #200')(piano_staff)
    return piano_staff

def make_staff_line_position_override_mark( clef_key ):
    #makes a LilyPondCommandMark that moves the staff lines according to a clef_key.
    #clef_key: 1 - 15va treble; 2 - normal treble; 3 - bass; 4 - treble and bass
    clef_dictionary = {1: schemetools.Scheme(18, 16, 14, 12, 10), 2: schemetools.Scheme(4, 2, 0, -2, -4), 3: schemetools.Scheme(-8, -10, -12, -14, -16), \
    4: schemetools.Scheme(4, 2, 0, -2, -4, -8, -10, -12, -14, -16)}
    staff_lines_scheme = clef_dictionary[clef_key]
    mark_string = "override Staff.StaffSymbol #'line-positions = #'" + str(staff_lines_scheme)
    staff_position_mark = marktools.LilyPondCommandMark(mark_string)
    return staff_position_mark

def make_clef_symbol_change_tuple( clef_key):
    #given a clef_key, returns a tuple of the three marks required to set clef symbol, position, and octavation.
    clef_glyph_dictionary = {1: ["#\"clefs.G\"", 12, 14], 2: ["#\"clefs.G\"", -2, 0], 3: ["#\"clefs.F\"", -10, 0], 4: ["#\"clefs.F\"", -10, 0] }
    glyph_list = clef_glyph_dictionary[ clef_key ]
    clef_symbol_string = glyph_list[0]
    position = "#" + str(glyph_list[1] )
    octavation = "#" + str(glyph_list[2] )
    return (clef_symbol_string, position, octavation)

def move_staff_lines(leaf, clef_key):
    #use: switches the position of staff lines at leaf according to clef_key (see above for description of key system)
    #algorithm: 
    #1. restarts staff
    #2. looks up clef symbol, position, and octavization in dictionary; attaching those marks to leaf 
    #3. attaches staff line position change to leaf
    marktools.LilyPondCommandMark("stopStaff")(leaf)
    marktools.LilyPondCommandMark("startStaff")(leaf)
    staff_position_mark = make_staff_line_position_override_mark( clef_key )
    staff_position_mark.attach(leaf)
    clef_symbol_change_tuple = make_clef_symbol_change_tuple( clef_key )
    symbol_string = clef_symbol_change_tuple[0]
    position = clef_symbol_change_tuple[1]
    octavation = clef_symbol_change_tuple[2]
    clef_string = "set Staff.clefGlyph = " + symbol_string
    marktools.LilyPondCommandMark(clef_string)(leaf)
    marktools.LilyPondCommandMark("set Staff.clefPosition = " + position)(leaf)
    marktools.LilyPondCommandMark("set Staff.clefOctavation = " + octavation)(leaf)

def format_staff( staff ):
    #staff.override.time_signature.stencil = False
    staff.override.beam.damping = 20000000
    staff.set.explicit_clef_visibility = schemetools.Scheme("end-of-line-invisible")
    staff.set.force_clef = True
    staff.override.beam.breakable = True
    for x, voice in enumerate(staff[1:]):
        if x % 2 == 1:
            marktools.LilyPondCommandMark('break', 'after')( voice[-1])
    contexttools.TempoMark((1,4), 88)(staff[0])
    contexttools.KeySignatureMark('d', 'major')( staff[0] )
    contexttools.KeySignatureMark('d', 'major')( staff[1] )
    contexttools.TimeSignatureMark((3,4))( staff[0] )
    #staff[0].override.dynamic_text.padding = 200
    marktools.BarLine('|.')(staff[1][-1])
    staff.override.vertical_axis_group.basic_distance = 1000

def format_score(score):
    #score.set.proportional_notation_duration = schemetools.SchemeMoment(1,8)
    score.set.tuplet_full_length = True
    #score.override.spacing_spanner.uniform_stretching = False
    #score.override.spacing_spanner.strict_note_spacing = False
    score.override.tuplet_bracket.padding = 2
    score.override.tuplet_bracket.staff_padding = 4
    score.override.tuplet_number.text = schemetools.Scheme('tuplet-number::calc-fraction-text')
    #score.override.bar_number.transparent = True
    score.override.metronome_mark.padding = 2
    
def format_lilypond_file(lilypond_file):
    lilypond_file.paper_block.paper_width = 8.5 * 25.4
    lilypond_file.paper_block.paper_height = 11 * 25.4
    lilypond_file.paper_block.top_margin = 1.0 * 25.4
    lilypond_file.paper_block.bottom_margin = 0.5 * 25.4
    lilypond_file.paper_block.left_margin = 1.0 * 25.4
    lilypond_file.paper_block.right_margin = 1.0 * 25.4
    lilypond_file.paper_block.ragged_bottom = False
    lilypond_file.global_staff_size = 16
    lilypond_file.layout_block.indent = 0
    lilypond_file.layout_block.ragged_right = False
    lilypond_file.paper_block.system_system_spacing = layouttools.make_spacing_vector(30, 0, 0, 0)
    directory = os.path.dirname(os.path.abspath(__file__))
    fontTree = os.path.join(directory,'fontTree.ly')
    lilypond_file.file_initial_user_includes.append(fontTree)
    context_block = lilypondfiletools.ContextBlock()
    context_block.context_name = r'PianoStaff \RemoveEmptyStaves'
    context_block.override.vertical_axis_group.remove_first = True
    lilypond_file.layout_block.context_blocks.append(context_block)

#layout and formatting - local

def format_melody(melody):
    marktools.LilyPondCommandMark('break','after')(melody[-1])
    contexttools.DynamicMark('f')(melody[0])
    marktools.BarLine('||')(melody[-1])

#staff and clef moving:

def add_staff_switches_to_voice( voice ):
    move_staff_lines_at_leaf(voice[0], 1)
    notes = list( iterationtools.iterate_notes_in_expr( voice ) )
    treble_notes = [x for x in notes if x.sounding_pitch.chromatic_pitch_number < 24 and x.sounding_pitch.chromatic_pitch_number >= -1]
    move_staff_lines_at_leaf(treble_notes[0], 2)
    bass_notes = [x for x in notes if x.sounding_pitch.chromatic_pitch_number < 0]
    move_staff_lines_at_leaf(bass_notes[0], 3)

def format_voice( voice ):
    spannertools.PhrasingSlurSpanner( voice[:])
    beamtools.BeamSpanner( voice[:] )
    add_staff_switches_to_voice( voice )
    voice.override.phrasing_slur.ratio = 0.6
    voice.override.phrasing_slur.height_limit = 20
    

#composition
def choose_distance_from_range_low(seed_interval):
    interval_width = seed_interval.number
    choice = randint(0, interval_width)
    return choice
    
def get_pitch_set_from_pitch_range_tuple( pitch_range_tuple ):
    numeric_pitch_range_tuple = (numeric_pitch_range_low, numeric_pitch_range_high)
    pitches = [ ]
    for value in range( numeric_pitch_range_tuple[0], numeric_pitch_range_tuple[1] ):
        pitch = pitchtools.NamedChromaticPitch(value)
        pitches.append(pitch)
    return pitches

def make_chord( bottom_pitch_number, numeric_pitch_range_high ):
    pitch_number = bottom_pitch_number
    bottom_pitch = pitchtools.NamedChromaticPitch( pitch_number  )
    bottom_interval_choices = [5, 7, 9]
    chord = Chord( [ bottom_pitch ], Duration(1,4) )
    bottom_interval_ambitus = choice(bottom_interval_choices)
    next_to_bottom_pitch = bottom_pitch + bottom_interval_ambitus
    chord.append( next_to_bottom_pitch )
    added_pitch = next_to_bottom_pitch
    while added_pitch.chromatic_pitch_number <= int(numeric_pitch_range_high * 2/3) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 3, 4 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    while added_pitch.chromatic_pitch_number <= int(numeric_pitch_range_high) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 1, 2 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    return chord   

def make_chords(number_of_chords, pitch_range_tuple):
    numeric_pitch_range_low = pitchtools.chromatic_pitch_name_to_chromatic_pitch_number( pitch_range_tuple[0] )
    numeric_pitch_range_high = pitchtools.chromatic_pitch_name_to_chromatic_pitch_number( pitch_range_tuple[1] )
    chords = [ ]
    for x in range(number_of_chords):
        distance_from_range_low = choose_distance_from_range_low( pitchtools.HarmonicChromaticInterval(7) )
        bottom_pitch_number = numeric_pitch_range_low + distance_from_range_low
        chord = make_chord( bottom_pitch_number, numeric_pitch_range_high )
        chords.append(chord)
    return chords

#def place_component_on_staffs(component, braced_staffs):
 #   #if 1 < len(component):
  #   #   place_tuplet_on_staffs( component, braced_staffs )
  #  elif isinstance(component, Rest):    
  #      place_rest_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Note):
  #      place_note_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Chord):
  #      place_note_on_staffs(component, braced_staffs) 

def get_range_bounds( voice ):
    pitch_numbers = [ x.written_pitch.chromatic_pitch_number for x in iterationtools.iterate_components_and_grace_containers_in_expr( voice.leaves, (Note, Chord) ) ]
    low = min(pitch_numbers)
    high = max(pitch_numbers)
    return (low, high)

def make_score( staff ):
    score = Score( [staff] )
    format_score(score)
    return score

def make_lilypond_file( staff ):
    score = make_score( staff )
    lilypond_file = lilypondfiletools.make_basic_lilypond_file(score)
    format_lilypond_file(lilypond_file)
    return lilypond_file

def make_chord_chart(number_of_chords, pitch_range_tuple):
    chords = make_chords(number_of_chords, pitch_range_tuple)
    lilypond_file = make_lilypond_file(chords)
    show(lilypond_file)
    play(lilypond_file)

def arpeggiate_chord( chord ):
    notes = [ ]
    pitches = chord.written_pitches
    ordered_pitches = [ ]
    for pitch in pitches:
        ordered_pitches.append( pitch )
    ordered_pitches.reverse()
    for pitch in ordered_pitches:
        note = Note(pitch, Duration(1,16))
        notes.append( note )
    voice = Voice(notes)
    format_voice(voice)
    return voice

def color_pitch( arpeggio, pitch):
    for note in iterationtools.iterate_notes_in_expr(arpeggio):
        if pitch == note.sounding_pitch:
            note.override.note_head.color = "red"
        

def contains_pitch( pitch_to_find, arpeggio ):
    pitches = set(pitchtools.list_named_chromatic_pitches_in_expr(arpeggio))
    if pitches.issuperset([ pitch_to_find ] ):
        return True
        
def format_subsequent_pitch( arpeggio, note, hidden_melody_tuple ):
    melody_note_dynamic = hidden_melody_tuple[1]
    original_dynamic = hidden_melody_tuple[0]
    marktools.Articulation("-",Up)(note)
    contexttools.DynamicMark(melody_note_dynamic)(note)
    index_of_the_note_after_that = note.parent.index(note)
    if index_of_the_note_after_that < len( arpeggio ) - 1:
        note_after_that = componenttools.get_nth_sibling_from_component(note, 1)
        contexttools.DynamicMark(original_dynamic)(note_after_that)

def emphasize_pitch( arpeggio, pitch_to_check, hidden_melody_tuple):
    for note in iterationtools.iterate_notes_in_expr(arpeggio):
        if pitch_to_check == note.sounding_pitch:
            format_subsequent_pitch( arpeggio, note, hidden_melody_tuple )
    
def find_melody_in_arpeggios( melody, arpeggio_voices, nth_time ):
    nth_time_dictionary = {0: [24, 'ppp', 'mf'], 1: [12, 'p', 'f'], 2: [0, 'mf', 'ff']}
    hidden_melody_tuple = nth_time_dictionary[nth_time]
    hidden_melody_transposition = hidden_melody_tuple[0]
    hidden_melody_tuple = hidden_melody_tuple[1:]
    selected_arpeggios = [ ]
    pitches = [ x.sounding_pitch for x in iterationtools.iterate_notes_in_expr( melody )]
    pitch_index = 0
    for arpeggio in arpeggio_voices:
        if pitch_index == len(pitches):
            break
        pitch_to_check = pitches[ pitch_index] + hidden_melody_transposition
        if contains_pitch( pitch_to_check, arpeggio):
            contexttools.DynamicMark(hidden_melody_tuple[0])(arpeggio[0])
            selected_arpeggios.append( arpeggio )
            #color_pitch( arpeggio, pitch_to_check)
            emphasize_pitch( arpeggio, pitch_to_check, hidden_melody_tuple)
            pitch_index += 1
    return selected_arpeggios
        
def arpeggiate_chords( chords ):
    arpeggio_voices = [ ]
    for chord in chords:
        arpeggio_voice = arpeggiate_chord( chord )
        arpeggio_voices.append( arpeggio_voice )
    return arpeggio_voices

def get_n_pitches_above_note_in_chord(note, chord, division):
    pitches = [x.written_pitch for x in chord if x.written_pitch.chromatic_pitch_number > note.written_pitch.chromatic_pitch_number]
    return pitches[ :division ]

def shift_pitches(pitches):
    shifted_pitches = []
    for pitch in pitches:
        pitch -= 12
        shifted_pitch = pitchtools.NamedChromaticPitch(pitch)
        shifted_pitches.append(shifted_pitch)
    shifted_pitches.reverse()
    return shifted_pitches
    
def pitch_tuplet(tuplet, note_chord_pair, division, x):
    note = note_chord_pair[0]
    chord = note_chord_pair[1]
    pitches = get_n_pitches_above_note_in_chord(note, chord, division)
    tuplet[0].written_pitch = note.written_pitch
    marktools.Articulation(">")(tuplet[0])
    note_pitch_pairs = zip(tuplet[1:], pitches)
    if x % 2 == 1:
        shifted_pitches = shift_pitches(pitches)
        note_pitch_pairs = zip(tuplet[1:], shifted_pitches)
    for pair in note_pitch_pairs:
        note = pair[0]
        pitch = pair[1]
        note.written_pitch = pitch
    
def split_melody(melody, division, chords):
    voice = Voice([Note(melody[0])])
    chords = chords[ : len(melody) ]
    note_chord_pairs = zip( melody[1:], chords )
    ratio = [1] * division
    for x, pair in enumerate(note_chord_pairs):
        tuplet = tuplettools.make_tuplet_from_duration_and_ratio(pair[0].duration, ratio)
        pitch_tuplet(tuplet, pair, division, x)
        voice.append(tuplet)
    marktools.BarLine('||')(voice[-1])
    return voice
        

def vary_melody( melody, divisions, chords ):
    voices_to_add = []
    for division in divisions:
        voice_to_add = split_melody(melody, division, chords )
        voices_to_add.append( voice_to_add)
    return voices_to_add
    
def make_transition_from_run( melody_one, decorated, run ):
    voice = Voice([])
    for x,choice in enumerate(run):
        if choice == 0:
            note = Note(melody_one[x])
            voice.append(note)
        elif choice == 1:
            tuplet_leaves = componenttools.copy_components_and_covered_spanners(decorated[x].music)
            tuplet = Tuplet(decorated[x].multiplier, tuplet_leaves)
            voice.append(tuplet)
    marktools.BarLine('||')(voice[-1])
    return voice

def make_prolated_echo_voice( melody, depth ):
    melody_copy = componenttools.copy_components_and_covered_spanners(melody[:])
    for x in range(depth):
        for leaf in melody_copy:
            leaftools.scale_preprolated_leaf_duration(leaf, 2)
        for leaf in melody_copy:
            leaf.written_pitch -= 12
    voice = Voice(melody_copy)
    return voice
        
def add_n_copies_of_melody_to_voice(melody_voice, n):
    copy_to_copy = componenttools.copy_components_and_covered_spanners(melody[:])
    for x in range(n):
        new_copy = componenttools.copy_components_and_covered_spanners(copy_to_copy)
        melody_voice.extend(new_copy)

def make_future_calendars( melody, pitch_range_tuple):
    top_voice = Voice([])
    recitation = componenttools.copy_components_and_covered_spanners(melody[:])
    top_voice.extend(recitation)
    for note in melody:
        note.written_pitch += 12
    staff = make_piano_staff()
    #format_melody(melody)
    add_n_copies_of_melody_to_voice( melody,1 )
    second_voice = make_prolated_echo_voice( melody, 1 )
    third_voice = make_prolated_echo_voice( recitation, 2)
    for leaf in third_voice:
        leaf.written_pitch += 12
    add_n_copies_of_melody_to_voice( melody,1 )
    for leaf in melody:
        marktools.LilyPondCommandMark('stemUp')(leaf)
    for leaf in second_voice:
        marktools.LilyPondCommandMark('stemDown')(leaf)
    top_voice.extend( melody )
    second_voice.insert(0, Rest(Duration(3,4)))
    third_voice.insert(0, Rest(Duration(3,4)))
    third_voice.insert(0, Rest(Duration(3,4)))
    contexttools.DynamicMark('f')(top_voice[0])
    contexttools.DynamicMark('f')(second_voice[1])
    contexttools.DynamicMark('f')(third_voice[2])
    staff[0].is_parallel = True
    top_voice.override.slur.direction = 1
    staff[0].append( top_voice )
    middle_voice = Voice([])
    middle_voice.extend(skiptools.Skip("s2.")*16)
    middle_voice.extend(second_voice)
    middle_voice.override.slur.direction = -1
    middle_voice.override.tie.direction = -1
    middle_voice.override.slur.free_slur_distance = 10
    staff[0].append( middle_voice )
    third_voice.override.slur.direction = -1
    staff[1].extend(Rest("r2.")*16)
    staff[1].append(third_voice)
    for line in staff:
        measures = componenttools.split_components_at_offsets(line.leaves, [Duration(3,4)], cyclic=True)
    del(middle_voice[-1])
    del(third_voice[-2:])
    format_staff(staff)
    lilypond_file = make_lilypond_file( staff )
    show(lilypond_file)
    #play(lilypond_file)

melody = Voice("e'4.( fs'8 e'4 a'4. b'8 a' b' cs''4 b'8 cs''16 b' a'8 fs' e'4.) fs'8( e' fs' a'4. b'8 a' b' cs'' b' a' fs' e' fs' a'4. b'8 a'4 a'2.) e''2( e''4 e'' cs'' b' cs'' b'8 cs''16 b' a'8 fs' e'4.) fs'8( e' fs' a'4. b'8 a' b' cs'' b' a' fs' e' fs' a'4. b'8 a'4 a'2.)")
make_future_calendars( melody, ("c", "c''''") )