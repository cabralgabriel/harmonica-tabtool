from music21 import note, chord, metadata, pitch

from constants.tunings import HARMONICA_TUNINGS

class ScoreEditor:
    def __init__(self, source):
        self.source = source
        self.harmonica_tunings = HARMONICA_TUNINGS

    def edit_metadata(self, score, title, key):
        title = title.replace("-", " ").replace("_", " ")
        if not score.metadata:
            score.insert(metadata.Metadata())
        score.metadata.movementName = title
        score.metadata.composer = 'Key of ' + key

        return score
    
    def chords_handler(self, score):
        count_removed_chords = 0
        count_removed_notes = 0
        for measure in score.getElementsByClass('Measure'):
            for element in measure.notesAndRests:
                if isinstance(element, chord.Chord):
                    count_removed_chords += 1
                    # Encontra a nota mais aguda (com maior oitava)
                    highest_pitch = None
                    max_pitch_value = float('-inf')  # Inicializa com o menor valor possível

                    for pitch in element.pitches:
                        if pitch.ps > max_pitch_value:
                            max_pitch_value = pitch.ps
                            highest_pitch = pitch

                    highest_note = highest_pitch
                    
                    # Remove todas as notas que não são a nota mais aguda
                    notes_to_remove = []
                    for pitch in element.pitches:
                        if pitch != highest_note:
                            notes_to_remove.append(pitch)

                    # Remove cada nota que não é a mais aguda do acorde
                    for note_to_remove in notes_to_remove:
                        count_removed_notes += 1
                        element.remove(note_to_remove)

        return score, count_removed_chords, count_removed_notes
    

    def harp_map(self, key, tuning, type):
        harp = {}
        start_pitch = pitch.Pitch(str(key))
        tuning_sys = self.harmonica_tunings[type].get(tuning, [])

        for note in tuning_sys:
            harp[start_pitch.ps] = note
            start_pitch = pitch.Pitch(start_pitch.ps + 1)

        return harp
    
    def label_notes(self, score, type, tuning, key, reduce_chords):
        if type == 'Diatonic':
            self.harmonica_mapping = self.harp_map(key, tuning, 'diatonic')
        elif type == 'Chromatic':
            self.harmonica_mapping = self.harp_map(key, tuning, 'chromatic')
        tab_in_text = ''

        for measure in score.getElementsByClass('Measure'):
            for element in measure.notes:
                if isinstance(element, note.Note):
                    #note_name = element.nameWithOctave # Name of the note
                    note_ps = element.pitch.ps
                    harmonica_note = self.harmonica_mapping.get(note_ps, ' ?')
                    element.addLyric(harmonica_note)
                    tab_in_text += f"{harmonica_note}"
                
                elif isinstance(element, chord.Chord):

                    if not reduce_chords.isChecked():
                        first_note = True
                        tab_in_text += f" ("
                        
                    line = 1
                    for pitch in reversed(element.pitches):
                        note_ps = pitch.ps
                        harmonica_note = self.harmonica_mapping.get(note_ps, ' ?')
                        element.addLyric(harmonica_note, lyricNumber=line)
                        
                        if not reduce_chords.isChecked():
                            if first_note:
                                harmonica_note = harmonica_note[1:]
                                first_note = False
                        tab_in_text += f"{harmonica_note}"
                        line += 1
                    
                    if not reduce_chords.isChecked():
                        tab_in_text += f")"
        
        return score, tab_in_text
    
    def filter_keys(self, score, tuning, key_options, char):
        """
        Filter key options based on the presence of a specific character in harmonica notes.

        Parameters
        ----------
        score : Score
            The musical score to analyze.
        tuning : str
            The harmonica tuning.
        key_options : list of tuples
            The key options to filter.
        char : str
            The character to check for in harmonica notes.

        Returns
        -------
        list of tuples
            The filtered key options.
        """
        filtered_keys = []

        for key_name, key in key_options:
            self.harmonica_mapping = self.harp_map(key, tuning, 'diatonic')
            
            remove_key = False
            for measure in score.getElementsByClass('Measure'):
                for element in measure.notes:
                    if isinstance(element, note.Note):
                        note_ps = element.pitch.ps
                        harmonica_note = self.harmonica_mapping.get(note_ps, '?')
                        if char in harmonica_note:
                            remove_key = True
                            break
                if remove_key:
                    break

            if not remove_key:
                filtered_keys.append((key_name, key))

        return filtered_keys
