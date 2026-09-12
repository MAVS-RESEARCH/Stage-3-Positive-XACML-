import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;
import java.util.Map;

import oasis.names.tc.xacml._3_0.core.schema.wd_17.Attribute;
import oasis.names.tc.xacml._3_0.core.schema.wd_17.AttributeValueType;
import oasis.names.tc.xacml._3_0.core.schema.wd_17.Attributes;
import oasis.names.tc.xacml._3_0.core.schema.wd_17.Request;
import org.ow2.authzforce.core.pdp.api.XmlUtils.XmlnsFilteringParser;
import org.ow2.authzforce.core.pdp.api.io.XacmlJaxbParsingUtils;
import org.ow2.authzforce.core.pdp.testutil.TestUtils;

/**
 * Parse-only proof driver for PC-XACML-S3+ hardening.
 *
 * <p>Unmarshals XACML request files with the frozen engine's own JAXB
 * parser factory (the exact first step of the native pipeline, also
 * used by {@code TestUtils.createRequest}) and prints the resulting
 * per-coordinate value bags. It never constructs a PDP engine,
 * evaluates no policy, and returns no decision. Arguments: pairs of
 * {@code <label>=<requestFile>} followed by {@code <outFile>}.
 */
public final class ParseProof
{
	private ParseProof()
	{
		// utility class
	}

	/**
	 * Unmarshals the requests and writes the observed bags.
	 *
	 * @param args label=request pairs then output file
	 * @throws Exception on any I/O or parse failure
	 */
	public static void main(final String[] args) throws Exception
	{
		if (args.length < 2)
		{
			System.err.println("usage: ParseProof <label>=<request>... <out>");
			System.exit(2);
		}
		final XmlnsFilteringParser unmarshaller = XacmlJaxbParsingUtils.getXacmlParserFactory(false).getInstance();
		final StringBuilder out = new StringBuilder();
		for (int i = 0; i < args.length - 1; i++)
		{
			final String[] parts = args[i].split("=", 2);
			final Request request = TestUtils.createRequest(Paths.get(parts[1]), unmarshaller);
			final Map<String, List<String>> bags = new TreeMap<>();
			for (final Attributes attributes : request.getAttributes())
			{
				for (final Attribute attribute : attributes.getAttributes())
				{
					final List<String> values = new ArrayList<>();
					for (final AttributeValueType value : attribute.getAttributeValues())
					{
						final List<java.io.Serializable> content = value.getContent();
						final StringBuilder text = new StringBuilder();
						for (final java.io.Serializable item : content)
						{
							text.append(item.toString());
						}
						values.add(value.getDataType() + "|" + text.toString());
					}
					bags.put(attributes.getCategory() + "\n" + attribute.getAttributeId() + "\n" + attribute.getIssuer(), values);
				}
			}
			out.append("[").append(parts[0]).append("]\n");
			for (final Map.Entry<String, List<String>> entry : bags.entrySet())
			{
				out.append(entry.getKey()).append(" => ").append(entry.getValue()).append("\n");
			}
		}
		Files.write(Paths.get(args[args.length - 1]), out.toString().getBytes(StandardCharsets.UTF_8));
		System.out.println("PARSE_PROOF_OK");
	}
}
