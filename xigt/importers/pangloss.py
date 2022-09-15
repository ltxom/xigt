from xml.etree import ElementTree
import xigt
from xigt.codecs import xigtxml

output_file = []


def xigt_import(inpath, outpath, options=None):
    output_file.append(outpath)
    tree = ElementTree.parse(inpath)
    phrase_list = []

    for phrase in tree.findall('S'):
        phrase_tier = ''
        words_tier = []
        morphemes_tier = []
        glosses_tier = []
        pos_tier = []
        translation_tier = ''

        for item in phrase.findall('W'):
            form = item.find('FORM').text
            words_tier.append(form)
            phrase_tier += form + ' '
            morphemes = []
            glosses = []
            if len(item.findall('M'))>0:
                for morpheme in item.findall('M'):
                    morphemes.append(morpheme.find('FORM').text)
                    for gloss in morpheme.findall('TRANSL'):
                        if list(gloss.attrib.values())[0] == 'en':
                            glosses.append(gloss.text)
            else:
                for gloss in item.findall('TRANSL'):
                    if list(gloss.attrib.values())[0] == 'en':
                        glosses.append(gloss.text)
            glosses_tier.append(glosses)
            morphemes_tier.append(morphemes)

        for translation in phrase.findall('TRANSL'):
            if list(translation.attrib.values())[0] == 'en':
                translation_tier = translation.text

        phrase_list.append({'phrase': phrase_tier, 'words': words_tier, 'morphemes': morphemes_tier, 'glosses':
            glosses_tier, 'translation': translation_tier})
    buildXML(phrase_list)


def buildXML(phrase_list):
    xxml = xigt.XigtCorpus()
    igt_counter = 1
    for phrase in phrase_list:
        igt = xigt.Igt(id='igt' + str(igt_counter))
        pid = 'p' + str(igt_counter)
        p_tier = xigt.Tier(type='phrases', id='p')
        w_tier = xigt.Tier(type='words', id='w', segmentation='p')
        m_tier = xigt.Tier(type='morphemes', id='m', segmentation='w')
        g_tier = xigt.Tier(type='glosses', id='g', alignment='m')
        t_tier = xigt.Tier(type='translations', id='t', alignment='p')

        p_tier.append(xigt.Item(id=pid, text=phrase['phrase']))
        word_id = 1
        left = 0
        right = 0
        for word in phrase['words']:
            right += len(word) - 1
            w_tier.append(xigt.Item(id='w' + str(word_id), text=word,
                                    segmentation=pid + '[' + str(left) + ',' + str(right) + ']'))
            left = right + 2
            right += 2
            word_id += 1

        word_id = 1
        for morpheme in phrase['morphemes']:
            morpheme_id = 1
            left = 0
            right = 0
            for m in morpheme:
                right += len(m) - 1
                m_tier.append(xigt.Item(id='m' + str(word_id) + '.' + str(morpheme_id), text=m,
                                        segmentation='w' + str(word_id) + '[' + str(left) + ':' + str(right) + ']'))
                right += 1
                left = right
                morpheme_id += 1
            word_id += 1

        word_id = 1
        for gloss in phrase['glosses']:
            gloss_id = 1
            for g in gloss:
                g_tier.append(xigt.Item(id='g' + str(word_id) + '.' + str(gloss_id), text=g,
                                        alignment='m' + str(word_id) + '.' + str(gloss_id)))
                gloss_id += 1
            word_id += 1
        t_tier.append(xigt.Item(id='t1', text=phrase['translation']))
        igt_counter += 1

        igt.append(p_tier)
        igt.append(w_tier)
        igt.append(m_tier)
        igt.append(g_tier)
        igt.append(t_tier)
        xxml.append(igt)
    xigtxml.dump(open(output_file[0], 'w', encoding='utf-8'), xxml)