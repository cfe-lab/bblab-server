from django.urls import path, include
from django.shortcuts import redirect

# I put the function here cause it looks nice, hope thats fine. (-_^)
def tool_redirect(request):
	return redirect('/django/wiki/')

urlpatterns = [
	path('quality_check/', include('tools.quality_check.urls')),
	path('unique_sequence/', include('tools.unique_sequence.urls')),
	path('sequencing_layout/', include('tools.sequencing_layout.urls')),
	path('guava_layout/', include('tools.guava_layout.urls')),
	path('codon_by_codon/', include('tools.codon_by_codon.urls')),
	path('qvalue/', include('tools.qvalue.urls')),
	path('fasta_converter/', include('tools.fasta_converter.urls')),
	path('text_to_columns/', include('tools.text_to_columns.urls')),
	path('translate_DNA/', include('tools.translate_DNA.urls')),
	path('HIV_genome/', include('tools.HIV_genome.urls')),
	path('variable_function/', include('tools.variable_function.urls')),
	path('best_prob_HLA_imputation/', include('tools.best_prob_HLA_imputation.urls')),
	path('phage_i_expanded/', include('tools.phage_i_expanded.urls')),
	path('phylodating/', include('tools.phylodating.urls')),
	# path('PHAGE_I_expanded_v2/', include('tools.PHAGE_I_expanded_v2.urls')),

	# BEGIN 2019-11-22 dmacmillan
	# path('test_phage/', include('tools.test_PHAGE_I_expanded_v2.urls')),
	# END

	# This tool is the code copied from "github.com/dmacmillan/PHAGE-I-expanded/releases/tag/v1.0.0b"
	# but converted to work with django.
	# path('test_b_PHAGE_I_expanded/', include('tools.test_b_PHAGE_I_expanded.urls')),

	path('tcr_distance/', include('tools.tcr_distance.urls')),
	path('tcr_visualizer/', include('tools.tcr_visualizer.urls')),
	path('', tool_redirect),
]

